// wabblespec-session-start.js — Claude Code SessionStart hook
// Runs once at session open. Writes flag, emits session context as system context.
//
// Claude Code injects SessionStart stdout as a system prompt addendum.
// Emit enough context that invariants don't need repeating per-turn.

'use strict';

const fs = require('fs');
const path = require('path');
const { FLAG_PATH, safeWriteFlag, readSessionState } = require('./wabblespec-config');

// ── Helpers ──────────────────────────────────────────────────────────────────

function readVersion() {
  try {
    return fs.readFileSync(
      path.join(process.cwd(), '.wabblespec', 'VERSION'), 'utf8'
    ).trim();
  } catch (e) { return 'unknown'; }
}

function readLastReceiptTimestamp() {
  try {
    const indexPath = path.join(
      process.cwd(), '.wabblespec', 'state', 'archive', 'receipt-index.json'
    );
    const data = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
    // Handle both array and {entries: [...]} shapes
    const entries = Array.isArray(data) ? data : (data.entries || []);
    if (entries.length > 0) {
      const last = entries[entries.length - 1];
      return last.completed_at || last.timestamp || null;
    }
    return null;
  } catch (e) { return null; }
}

function readL8GateStatus() {
  try {
    const gatePath = path.join(
      process.cwd(), '.wabblespec', 'engine', 'shared', 'references', 'l8-corpus-gate.md'
    );
    const content = fs.readFileSync(gatePath, 'utf8');
    // Look for "status: MET" or "gate_status: MET" in first 20 lines
    const lines = content.split('\n').slice(0, 20);
    for (const line of lines) {
      if (/met/i.test(line)) return 'MET';
      if (/not.?met/i.test(line)) return 'NOT MET';
    }
    return null;
  } catch (e) { return null; }
}

// ── Main ─────────────────────────────────────────────────────────────────────

const version = readVersion();
const state = readSessionState();

// Write flag
const flagContent = (state && state.task_id)
  ? `task:${state.task_id}|waves:${state.waves_completed || 0}|phase:${state.phase || 'unknown'}`
  : 'idle';
safeWriteFlag(FLAG_PATH, flagContent);

// Build context output
const lines = [];
lines.push(`WABBLESPEC v${version} — session started`);

if (state && state.task_id) {
  // Active task session
  const wavePlan = state.wave_plan || {};
  const totalWaves = Array.isArray(wavePlan.waves) ? wavePlan.waves.length : '?';
  const wavesDone = state.waves_completed || 0;

  lines.push('');
  lines.push(`ACTIVE TASK: ${state.task_id}`);
  lines.push(`Phase: ${state.phase || 'unknown'} | Waves: ${wavesDone}/${totalWaves} complete`);
  if (state.active_modules && state.active_modules.length) {
    lines.push(`Active modules: ${state.active_modules.join(', ')}`);
  }
  if (state.revise_cycles && state.revise_cycles > 0) {
    lines.push(`Revise cycles used: ${state.revise_cycles}/3 (I4)`);
  }
  lines.push('');
  lines.push('ENFORCEMENT ACTIVE:');
  lines.push('  I1  — NO EXECUTION outside a locked spec. Phase 2 does not begin until Phase 1 spec is locked.');
  lines.push('  I4  — NO PHASE ADVANCE without a passing verification gate. Max 3 REVISE cycles; cycle 3 forces Attestation.');
  lines.push('  I10 — NO IMPLIED COMPLETION. Every non-trivial output writes a receipt before the phase closes.');
  lines.push('  I11 — NO WRITES to .wabblespec/ from product-space tasks. Framework modules own that space.');
  lines.push('  Guard is active. Pre-tool-use hooks enforcing staleness + invariants.');
} else {
  // No open session
  const lastTs = readLastReceiptTimestamp();
  const l8Status = readL8GateStatus();

  lines.push('');
  lines.push('No open task session.');
  lines.push('To start work: run Recipe with a task card.');
  if (lastTs) lines.push(`Last receipt: ${lastTs}`);
  if (l8Status) lines.push(`L8 evolution gate: ${l8Status}`);
  lines.push('');
  lines.push('Key invariants:');
  lines.push('  I1  — NO EXECUTION outside a locked spec.');
  lines.push('  I10 — NO IMPLIED COMPLETION. Non-trivial output requires a receipt.');
  lines.push('  I11 — NO WRITES to .wabblespec/ from product-space tasks.');
}

// ── Compaction recovery warning ──────────────────────────────────────────────
// When context is compacted mid-workflow, the summarization may lose pending-approval state.
// Re-inject a re-confirm reminder so the agent does not silently bypass approval gates.
try {
  const stdinData = fs.readFileSync(0, { encoding: 'utf-8', flag: 'r' }).trim();
  if (stdinData) {
    const eventData = JSON.parse(stdinData);
    if (eventData && eventData.source === 'compact') {
      lines.push('');
      lines.push('CONTEXT COMPACTED - APPROVAL STATE CHECK:');
      lines.push('If you were waiting for user approval at any gate (plan review, wave execute, or attestation),');
      lines.push('you MUST re-confirm with the user before proceeding. Do NOT assume approval was given.');
      lines.push('Ask the user to confirm approval before continuing work.');
    }
  }
} catch (e) { /* silent-fail — stdin may not be available in all invocation contexts */ }

// ── Review queue cross-machine reconciliation ────────────────────────────────
// Run review-sync.py to reconcile any entries in queue.json that arrived via
// git pull from other machines. Silent-fail — never blocks session start.
try {
  const { execFileSync } = require('child_process');
  const syncScript = path.join(
    process.cwd(), '.wabblespec', 'engine', 'shared', 'scripts', 'review-sync.py'
  );
  if (fs.existsSync(syncScript)) {
    execFileSync(process.execPath || 'python', [syncScript, '--no-pull', '--verbose'],
      { cwd: process.cwd(), timeout: 30000, stdio: 'pipe' });
  }
} catch (e) { /* silent-fail */ }

// ── Wave review daemon + pending reviews ─────────────────────────────────────

function readPendingReviews() {
  try {
    const pendingDir = path.join(process.cwd(), '.wabblespec', 'state', 'reviews', 'pending');
    if (!fs.existsSync(pendingDir)) return [];
    return fs.readdirSync(pendingDir)
      .filter(f => f.endsWith('.json'))
      .map(f => {
        try {
          const job = JSON.parse(fs.readFileSync(path.join(pendingDir, f), 'utf8'));
          return { file: f, ref: job.resolved_ref, type: job.review_type, lines: job.diff_lines };
        } catch (e) { return null; }
      })
      .filter(Boolean);
  } catch (e) { return []; }
}

function readDaemonStatus() {
  try {
    const pidPath = path.join(process.cwd(), '.wabblespec', 'state', 'reviews', 'daemon', 'daemon.pid');
    if (!fs.existsSync(pidPath)) return 'STOPPED';
    const pid = parseInt(fs.readFileSync(pidPath, 'utf8').trim(), 10);
    // On Unix we'd send signal 0; on Windows just check if PID file is recent (<60s)
    const stat = fs.statSync(pidPath);
    const ageMs = Date.now() - stat.mtimeMs;
    return ageMs < 60000 ? `RUNNING (pid=${pid})` : `UNKNOWN (pid=${pid}, pid file stale)`;
  } catch (e) { return 'STOPPED'; }
}

const pendingReviews = readPendingReviews();
const daemonStatus = readDaemonStatus();

const daemonRunning = daemonStatus.startsWith('RUNNING');

if (pendingReviews.length > 0 && !daemonRunning) {
  // Daemon not running — surface pending reviews for inline session review
  lines.push('');
  lines.push(`PENDING WAVE REVIEWS (${pendingReviews.length}) — daemon not running:`);
  for (const r of pendingReviews) {
    lines.push(`  ${r.ref}  type=${r.type}  diff_lines=${r.lines}`);
  }
  lines.push('  Run /wave-review to review inline, or start the daemon:');
  lines.push('  python .wabblespec/engine/shared/scripts/review-daemon.py start');
} else if (pendingReviews.length > 0) {
  // Daemon is running — it will process them; just inform
  lines.push('');
  lines.push(`WAVE REVIEWER: ${daemonStatus} | ${pendingReviews.length} pending (daemon processing)`);
} else if (!daemonRunning) {
  lines.push('');
  lines.push('WAVE REVIEWER: daemon not running. Start: python .wabblespec/engine/shared/scripts/review-daemon.py start');
}

process.stdout.write(lines.join('\n'));
