// wabblespec-precompact.js — Claude Code PreCompact hook
// Fires before every auto or manual context compaction.
//
// Purpose: injects a compact instruction into the compaction prompt that
// directs the compaction agent to preserve WabbleSpec task state in the
// summary. Without this, compaction summaries may omit wave progress,
// current phase, and active receipt chain status — causing Executor to
// lose position after a /compact.
//
// Output contract:
//   - Active task:   {"customSystemPrompt": "<instruction text>"}
//   - No active task or error: {} (pass through silently)
//
// Silent-fail contract: all errors caught; never emits non-zero exit or
// blocks the compaction. Hook failures must not interrupt the session.

'use strict';

const { readSessionState, readFlag, FLAG_PATH } = require('./wabblespec-config');

process.stdin.resume(); // drain stdin; PreCompact hooks receive a JSON payload

let input = '';
process.stdin.on('data', d => { input += d; });
process.stdin.on('end', () => {
  try {
    const state = readSessionState();
    const flag  = readFlag(FLAG_PATH);

    // Only inject when there is an active task with a known task_id
    if (!state || !state.task_id || !flag || flag === 'idle') {
      process.stdout.write('{}');
      return;
    }

    const taskId    = state.task_id   || 'unknown';
    const phase     = state.phase     || 'unknown';
    const wavesDone = state.waves_completed || 0;
    const wavePlan  = state.wave_plan || {};
    const total     = Array.isArray(wavePlan.waves) ? wavePlan.waves.length : '?';
    const nextWave  = (typeof wavesDone === 'number') ? wavesDone + 1 : '?';

    // Compact instruction: concise (~180 tokens). Tells the compaction agent
    // what WabbleSpec state to preserve in its summary so Executor can resume
    // correctly after compaction.
    const instruction = [
      '[WabbleSpec PreCompact — task state to preserve in summary]',
      `Task: ${taskId} | Phase: ${phase} | Waves complete: ${wavesDone}/${total}`,
      `Next wave on resume: wave ${nextWave}`,
      'Include in summary: current wave number, phase name, last receipt type written.',
      'Active invariants: I1 (spec is source of truth), I4 (verification explicit),',
      '  I10 (receipts required for all non-trivial execution), I11 (no product writes to .wabblespec/).',
      'Executor resumes ownership of remaining waves after compaction completes.',
    ].join('\n');

    process.stdout.write(JSON.stringify({ customSystemPrompt: instruction }));

  } catch (e) {
    // Silent fail — never block compaction
    process.stdout.write('{}');
  }
});
