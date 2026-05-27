// wabblespec-prompt-guard.js — Claude Code UserPromptSubmit hook
// Runs before every user prompt is processed.
//
// Two responsibilities (informational only — never blocks):
//   1. If active task session with completed waves: reinforce wave progress
//      to prevent mid-wave drift (model forgetting it is inside Executor).
//   2. If no active session and prompt looks like a task-start: remind to
//      run Recipe first so Guard is active during execution.

'use strict';

const { readSessionState, readFlag, FLAG_PATH } = require('./wabblespec-config');

// Patterns indicating the user intends to start a new build task
const TASK_START_PATTERNS = [
  /\bimplement\b/i,
  /\bbuild\s+(a|the|this|new)\b/i,
  /\bcreate\s+(a\s+)?new\s+module\b/i,
  /\badd\s+(a\s+)?feature\b/i,
  /\blet'?s\s+start\s+(on|with|building)\b/i,
  /\bbegin\s+work\s+on\b/i,
  /\bwrite\s+(a\s+)?new\s+module\b/i,
  /\bscaffold\s+(a|the|new)\b/i,
];

// Read prompt from stdin (Claude Code sends {"prompt": "..."} as JSON)
let input = '';
process.stdin.on('data', d => { input += d; });
process.stdin.on('end', () => {
  try {
    const payload = JSON.parse(input);
    const prompt = payload.prompt || '';

    const state = readSessionState();
    const flag = readFlag(FLAG_PATH);

    // 1. Active session with wave progress — reinforce state
    if (state && state.task_id && flag && flag !== 'idle') {
      const wavesDone = state.waves_completed || 0;
      if (wavesDone > 0) {
        const wavePlan = state.wave_plan || {};
        const totalWaves = Array.isArray(wavePlan.waves) ? wavePlan.waves.length : '?';
        const output = `[WabbleSpec] Resuming active task — ${wavesDone}/${totalWaves} waves complete, phase: ${state.phase || 'unknown'}. Executor holds the remaining waves; continue from the last wave checkpoint.`;
        process.stdout.write(JSON.stringify({ additionalContext: output }));
        return;
      }
    }

    // 2. No active session + prompt looks like task-start — remind to run Recipe
    const looksLikeTaskStart = TASK_START_PATTERNS.some(p => p.test(prompt));
    if (looksLikeTaskStart && (!state || !state.task_id)) {
      const output = [
        '[WabbleSpec] Session inactive — Recipe activates Guard and enables full invariant enforcement.',
        'Common rationalisations that signal an invariant violation is forming:',
        '  "This is too simple to need a receipt"          → I10: complexity is not the gate; non-trivial is.',
        '  "I know what the spec means, I can proceed"     → I1: locked spec is the gate, not interpretation.',
        '  "I just need to fix one thing in .wabblespec/"  → I11: framework space; no product-task exceptions.',
        'Start a task card via Recipe, then retry this prompt.',
      ].join('\n');
      process.stdout.write(JSON.stringify({ additionalContext: output }));
      return;
    }

  } catch (e) { /* silent fail — never block on parse errors */ }

  // No output — pass through silently
  process.stdout.write('{}');
});
