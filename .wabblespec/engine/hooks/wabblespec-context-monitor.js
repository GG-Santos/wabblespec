// WabbleSpec Context Monitor — PostToolUse hook
//
// Reads context metrics from the statusline bridge file and injects
// advisory warnings when context is running low. Makes the agent aware
// of context limits (the statusline only shows the user).
//
// Architecture:
//   1. The statusline hook writes metrics to /tmp/claude-ctx-{session_id}.json
//   2. This hook reads those metrics after each tool use
//   3. When remaining context drops below thresholds, it injects a warning
//      as additionalContext that the agent sees in its conversation
//
// Thresholds (from economy/rules/cold-start.md — Context degradation tiers):
//   WARNING  (remaining <= 35%): context is DEGRADING — avoid new complex work
//   CRITICAL (remaining <= 25%): context is POOR — checkpoint immediately
//
// Debounce: 5 tool calls between warnings at the same severity level.
// Severity escalation (WARNING → CRITICAL) bypasses debounce.
// Stale metrics (older than 60 seconds) are ignored.
//
// On CRITICAL with an active WabbleSpec session: writes context_exhaustion_pct
// to state.json as a breadcrumb for session resume.
//
// Silent-fail contract: all errors caught and swallowed. Never blocks tool execution.

'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const WARNING_THRESHOLD = 35;   // remaining_percentage <= 35% → DEGRADING tier
const CRITICAL_THRESHOLD = 25;  // remaining_percentage <= 25% → POOR tier
const STALE_SECONDS = 60;       // ignore metrics older than this
const DEBOUNCE_CALLS = 5;       // min tool uses between same-severity warnings

let input = '';
// Timeout guard: if stdin does not close within 10s, exit silently.
// Prevents hanging if piping is slow or broken.
const stdinTimeout = setTimeout(() => process.exit(0), 10000);
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  clearTimeout(stdinTimeout);
  try {
    const data = JSON.parse(input);
    const sessionId = data.session_id;

    if (!sessionId) {
      process.exit(0);
    }

    // Reject session IDs containing path traversal sequences.
    // session_id is used to construct file paths in /tmp — an unsanitized
    // value could escape the temp directory and read arbitrary files.
    if (/[/\\]|\.\./.test(sessionId)) {
      process.exit(0);
    }

    // Check if context warnings are disabled via WabbleSpec session config.
    const cwd = data.cwd || process.cwd();
    try {
      const statePath = path.join(cwd, '.wabblespec', 'state', 'session', 'state.json');
      const stateData = JSON.parse(fs.readFileSync(statePath, 'utf8'));
      if (stateData && stateData.context_warnings_disabled === true) {
        process.exit(0);
      }
    } catch (e) {
      // Missing or unparseable state.json → proceed with warnings enabled (safe default)
    }

    const tmpDir = os.tmpdir();
    const metricsPath = path.join(tmpDir, `claude-ctx-${sessionId}.json`);

    // No metrics file → this is a subagent or fresh session without statusline data.
    let metricsRaw;
    try {
      metricsRaw = fs.readFileSync(metricsPath, 'utf8');
    } catch (e) {
      if (e && e.code === 'ENOENT') process.exit(0);
      throw e;
    }

    const metrics = JSON.parse(metricsRaw);
    const now = Math.floor(Date.now() / 1000);

    // Ignore stale metrics.
    if (metrics.timestamp && (now - metrics.timestamp) > STALE_SECONDS) {
      process.exit(0);
    }

    const remaining = metrics.remaining_percentage;
    const usedPct = metrics.used_pct;

    // No warning needed — context is in PEAK or GOOD tier.
    if (remaining > WARNING_THRESHOLD) {
      process.exit(0);
    }

    // Debounce: check whether we warned recently at this level.
    const warnPath = path.join(tmpDir, `claude-ctx-${sessionId}-warned.json`);
    let warnData = { callsSinceWarn: 0, lastLevel: null };
    let firstWarn = true;

    try {
      warnData = JSON.parse(fs.readFileSync(warnPath, 'utf8'));
      firstWarn = false;
    } catch (e) {
      // Missing or corrupted sentinel → treat as first warning
    }

    warnData.callsSinceWarn = (warnData.callsSinceWarn || 0) + 1;

    const isCritical = remaining <= CRITICAL_THRESHOLD;
    const currentLevel = isCritical ? 'critical' : 'warning';

    // Severity escalation (WARNING → CRITICAL) bypasses debounce.
    const severityEscalated = currentLevel === 'critical' && warnData.lastLevel === 'warning';

    if (!firstWarn && warnData.callsSinceWarn < DEBOUNCE_CALLS && !severityEscalated) {
      // Update counter and exit without warning.
      fs.writeFileSync(warnPath, JSON.stringify(warnData));
      process.exit(0);
    }

    // Reset debounce counter.
    warnData.callsSinceWarn = 0;
    warnData.lastLevel = currentLevel;
    fs.writeFileSync(warnPath, JSON.stringify(warnData));

    // Detect if a WabbleSpec task is active (state.json with enforcement_active: true).
    const statePath = path.join(cwd, '.wabblespec', 'state', 'session', 'state.json');
    const isWabbleSpecActive = (() => {
      try {
        const stateData = JSON.parse(fs.readFileSync(statePath, 'utf8'));
        return stateData && stateData.enforcement_active === true;
      } catch (e) {
        return false;
      }
    })();

    // On CRITICAL with active WabbleSpec session: write context_exhaustion_pct breadcrumb
    // for session resume. Fire-and-forget subprocess — does not block the hook.
    // Only fires once per CRITICAL event, guarded by criticalRecorded.
    if (isCritical && isWabbleSpecActive && !warnData.criticalRecorded) {
      try {
        const sessionStateScript = path.join(cwd, '.wabblespec', 'engine', 'shared', 'scripts', 'session-state.py');
        const safeUsedPct = Number(usedPct) || 0;
        spawn(
          process.execPath.replace('node', 'python').replace('node.exe', 'python'),
          [sessionStateScript, 'set', 'context_exhaustion_pct', String(safeUsedPct)],
          { cwd, detached: true, stdio: 'ignore' }
        ).unref();
        warnData.criticalRecorded = true;
        fs.writeFileSync(warnPath, JSON.stringify(warnData));
      } catch (e) {
        // Non-critical — state recording failure must not break the hook
      }
    }

    // Build advisory message. Always advisory — never imperative commands
    // that override user preferences.
    let message;
    if (isCritical) {
      message = isWabbleSpecActive
        ? `CONTEXT CRITICAL (POOR tier): Usage at ${usedPct}%. Remaining: ${remaining}%. ` +
          'Context is nearly exhausted. Do NOT start new waves or complex work. ' +
          'If mid-wave, complete the current step and surface CONTEXT_EXHAUSTION. ' +
          'WabbleSpec session state is tracked in state.json.'
        : `CONTEXT CRITICAL (POOR tier): Usage at ${usedPct}%. Remaining: ${remaining}%. ` +
          'Context is nearly exhausted. Inform the user and ask how to proceed. ' +
          'Do NOT autonomously write handoff files unless explicitly asked.';
    } else {
      message = isWabbleSpecActive
        ? `CONTEXT WARNING (DEGRADING tier): Usage at ${usedPct}%. Remaining: ${remaining}%. ` +
          'Avoid starting new waves or complex reads. Skip optional enrichment steps ' +
          '(context7, graph queries). If approaching a wave boundary, consider completing ' +
          'the current wave and pausing before the next.'
        : `CONTEXT WARNING (DEGRADING tier): Usage at ${usedPct}%. Remaining: ${remaining}%. ` +
          'Prefer frontmatter reads. Avoid starting new complex work. Delegate aggressively.';
    }

    const output = {
      hookSpecificOutput: {
        hookEventName: 'PostToolUse',
        additionalContext: message
      }
    };

    process.stdout.write(JSON.stringify(output));

  } catch (e) {
    // Silent fail — never block tool execution
    process.exit(0);
  }
});
