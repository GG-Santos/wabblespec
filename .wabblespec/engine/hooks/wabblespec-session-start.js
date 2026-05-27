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
  lines.push('  I1  — spec is single source of truth; no execution outside spec');
  lines.push('  I10 — every non-trivial output requires a receipt; implied completion prohibited');
  lines.push('  I11 — do not write to .wabblespec/ directly; framework modules own writes there');
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
  lines.push('  I1  — spec is single source of truth');
  lines.push('  I10 — receipts are operational artifacts; implied completion prohibited');
  lines.push('  I11 — .wabblespec/ is framework space; never write there from product tasks');
}

process.stdout.write(lines.join('\n'));
