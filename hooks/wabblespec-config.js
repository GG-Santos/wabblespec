// wabblespec-config.js — shared hook utilities
// CommonJS module (package.json in this directory sets {"type": "commonjs"})
// Prevents ESM/CJS conflict when ancestor package.json declares "type": "module"

'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const FLAG_PATH = path.join(claudeDir, '.wabblespec-session');

// Session state path is relative to the CWD where hooks are invoked (the repo root)
const SESSION_STATE_PATH = path.join(
  process.cwd(), '.wabblespec', 'session', 'state.json'
);

/**
 * Symlink-safe atomic flag write.
 * Refuses if the target path or its immediate parent is a symlink.
 * Creates with mode 0600. Silent-fails on any filesystem error.
 */
function safeWriteFlag(flagPath, content) {
  try {
    // Refuse if target is a symlink
    try {
      const stat = fs.lstatSync(flagPath);
      if (stat.isSymbolicLink()) return;
    } catch (e) { /* does not exist — OK */ }

    // Refuse if parent is a symlink
    const parent = path.dirname(flagPath);
    try {
      const pstat = fs.lstatSync(parent);
      if (pstat.isSymbolicLink()) return;
    } catch (e) { return; } // parent does not exist

    const tmp = flagPath + '.tmp.' + process.pid;
    fs.writeFileSync(tmp, String(content), { mode: 0o600 });
    fs.renameSync(tmp, flagPath);
  } catch (e) { /* silent fail */ }
}

/**
 * Read and parse session/state.json. Returns null if absent or unparseable.
 */
function readSessionState() {
  try {
    const raw = fs.readFileSync(SESSION_STATE_PATH, 'utf8');
    return JSON.parse(raw);
  } catch (e) {
    return null;
  }
}

/**
 * Read flag file contents. Returns null if absent or unreadable.
 */
function readFlag(flagPath) {
  try {
    return fs.readFileSync(flagPath, 'utf8').trim();
  } catch (e) {
    return null;
  }
}

module.exports = { claudeDir, FLAG_PATH, safeWriteFlag, readSessionState, readFlag };
