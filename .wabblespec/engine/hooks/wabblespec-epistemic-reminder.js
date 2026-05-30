// wabblespec-epistemic-reminder.js — PostToolUse hook for Grep calls.
//
// Fires after every Grep tool call. Emits a systemMessage reminding the agent
// to read the actual file before claiming existence, behavior, or absence based
// on grep output.
//
// Source: continuous-claude-v3 epistemic-reminder hook pattern.
//
// Output contract:
//   - Grep tool:  { "systemMessage": "<reminder text>" }
//   - Other tools: {} (pass-through, do not interfere)
//   - Error:       {} (silent-fail contract — never blocks)

'use strict';

let input = '';
process.stdin.on('data', d => { input += d; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input || '{}');

    // Only fire for Grep (tolerate both 'tool' and 'toolName' keys)
    const toolName = data.tool || data.toolName || '';
    if (toolName !== 'Grep') {
      process.stdout.write('{}');
      return;
    }

    const msg = [
      '[Epistemic Reminder] Grep result received. Classify before asserting:',
      '  ✓ VERIFIED   — Read the actual file at the matched path to confirm.',
      '  ? INFERRED   — Grep matched but file not read; treat as hypothesis only.',
      '  ✗ UNCERTAIN  — Pattern not found does not prove absence (grep may truncate).',
      '',
      'Grep shows excerpts, not full file content. A match inside a comment,',
      'string literal, or disabled block is not a behavioral claim.',
      'Read the matched file before asserting what the code does or does not do.',
    ].join('\n');

    process.stdout.write(JSON.stringify({ systemMessage: msg }));

  } catch (_) {
    process.stdout.write('{}');
  }
});
