// visual-companion/server.js — Zero-dependency brainstorm visual companion
//
// Serves a localhost HTTP server that renders graphviz dot notation to SVG
// on demand, enabling inline diagram rendering during brainstorm sessions.
//
// Usage:
//   node server.js [--port 7331]
//
// Endpoints:
//   GET  /         — status page (lists available endpoints)
//   POST /render   — body: {"dot": "<graphviz dot source>"} → SVG string
//   GET  /ping     — health check → {"ok": true}
//
// Dependencies: Node.js stdlib only. Graphviz `dot` binary must be in PATH
// for SVG rendering. Falls back to returning the dot source if dot is unavailable.
//
// Silent-fail design: all errors return JSON {error: "..."}, never crash the server.

'use strict';

const http = require('http');
const { execFile } = require('child_process');

// ── CLI args ────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
let port = 7331;
for (let i = 0; i < args.length; i++) {
  if ((args[i] === '--port' || args[i] === '-p') && args[i + 1]) {
    port = parseInt(args[i + 1], 10) || port;
  }
}

// ── Helpers ─────────────────────────────────────────────────────────────────

function readBody(req, cb) {
  const chunks = [];
  req.on('data', c => chunks.push(c));
  req.on('end', () => cb(null, Buffer.concat(chunks).toString('utf8')));
  req.on('error', cb);
}

function renderDot(dotSource, cb) {
  execFile('dot', ['-Tsvg'], { timeout: 10000 }, (err, stdout, stderr) => {
    if (err) {
      // dot not available -- return the source with a note
      cb(null, `<!-- dot binary not available; raw source below -->\n<pre>${dotSource.replace(/</g, '&lt;')}</pre>`);
    } else {
      cb(null, stdout);
    }
  });

  // pipe dot source via stdin
  // (execFile doesn't support stdin directly -- use spawn for real rendering)
}

function renderDotWithStdin(dotSource, cb) {
  const { spawn } = require('child_process');
  const proc = spawn('dot', ['-Tsvg'], { timeout: 10000 });
  const chunks = [];
  const errChunks = [];

  proc.stdout.on('data', c => chunks.push(c));
  proc.stderr.on('data', c => errChunks.push(c));
  proc.on('error', () => {
    // dot not installed
    cb(null, `<pre style="font-family:monospace;background:#f5f5f5;padding:1em">${dotSource.replace(/&/g,'&amp;').replace(/</g,'&lt;')}</pre>`);
  });
  proc.on('close', code => {
    if (code === 0) {
      cb(null, Buffer.concat(chunks).toString('utf8'));
    } else {
      const errMsg = Buffer.concat(errChunks).toString('utf8');
      cb(null, `<pre style="color:red">Graphviz error:\n${errMsg}</pre>`);
    }
  });

  proc.stdin.write(dotSource);
  proc.stdin.end();
}

function sendJson(res, status, obj) {
  const body = JSON.stringify(obj);
  res.writeHead(status, { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) });
  res.end(body);
}

function sendHtml(res, body) {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(body);
}

// ── Routes ───────────────────────────────────────────────────────────────────

const INDEX_HTML = `<!DOCTYPE html>
<html><head><title>WabbleSpec Visual Companion</title>
<style>body{font-family:sans-serif;max-width:800px;margin:2em auto;padding:0 1em}
textarea{width:100%;height:120px;font-family:monospace}
#svg-output{border:1px solid #ddd;padding:1em;min-height:100px;margin-top:1em}
</style></head><body>
<h2>WabbleSpec Visual Companion</h2>
<p>Paste <a href="https://graphviz.org/doc/info/lang.html">graphviz dot</a> source below to render a diagram.</p>
<textarea id="dot" placeholder="digraph G { A -> B -> C }"></textarea><br>
<button onclick="render()">Render</button>
<div id="svg-output"></div>
<script>
async function render() {
  const dot = document.getElementById('dot').value;
  const res = await fetch('/render', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({dot})});
  const data = await res.json();
  document.getElementById('svg-output').innerHTML = data.svg || data.error || 'no output';
}
</script>
</body></html>`;

function handleRequest(req, res) {
  const url = new URL(req.url, `http://localhost:${port}`);

  if (req.method === 'GET' && url.pathname === '/') {
    sendHtml(res, INDEX_HTML);

  } else if (req.method === 'GET' && url.pathname === '/ping') {
    sendJson(res, 200, { ok: true, port });

  } else if (req.method === 'POST' && url.pathname === '/render') {
    readBody(req, (err, body) => {
      if (err) { sendJson(res, 400, { error: 'read error' }); return; }
      let dotSource = '';
      try {
        dotSource = JSON.parse(body).dot || '';
      } catch (_) {
        dotSource = body; // accept raw dot source too
      }
      if (!dotSource.trim()) { sendJson(res, 400, { error: 'empty dot source' }); return; }

      renderDotWithStdin(dotSource, (err2, svg) => {
        if (err2) { sendJson(res, 500, { error: String(err2) }); return; }
        sendJson(res, 200, { svg });
      });
    });

  } else {
    sendJson(res, 404, { error: 'not found' });
  }
}

// ── Start ────────────────────────────────────────────────────────────────────

const server = http.createServer(handleRequest);
server.listen(port, '127.0.0.1', () => {
  console.log(`Visual companion running at http://127.0.0.1:${port}/`);
  console.log('POST /render with {"dot": "<source>"} to render a diagram.');
  console.log('Press Ctrl+C to stop.');
});
