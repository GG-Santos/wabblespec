# WabbleSpec Memory Init

Guide the user through a complete WabbleSpec Memory setup. Follow each step in
order, stopping to report errors and attempt remediation before proceeding.

## Step 1: Check Python version

Run `python3 --version` (or `python --version` on Windows) and confirm the
version is 3.9 or higher. If Python is not found or the version is too old,
tell the user they need Python 3.9+ installed and stop.

## Step 2: Check if memory is available

Run `memory --version`. If it succeeds, the CLI is on PATH. Report the installed
version and skip to Step 4.

If `memory --version` fails inside a WabbleSpec checkout, try
`python scripts/memory.py --version`. If the checkout launcher works, use
`python scripts/memory.py` for the remaining CLI commands and continue to
Step 4.

If neither command works, continue to Step 3.

## Step 3: Install the internal memory package

This is an internal package in the WabbleSpec checkout, not the old
`wabblespec_memory` public command surface. From the repo root, run:

    python -m pip install -e packages/memory

### Error handling -- install failures

If the install command fails, try these fallbacks in order:

1. Try `pip install -e packages/memory`.
2. Try `pip3 install -e packages/memory`.
3. Try `python3 -m pip install -e packages/memory`.
4. If the error mentions missing build tools or compilation failures (commonly
   from chromadb or its native dependencies):
   - On Linux/macOS: suggest `sudo apt-get install build-essential python3-dev`
     (Debian/Ubuntu) or `xcode-select --install` (macOS)
   - On Windows: suggest installing Microsoft C++ Build Tools from
     https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Then retry the install command
5. If all attempts fail, report the error clearly and stop.

## Step 4: Ask for project directory

Ask the user which project directory they want to initialize with WabbleSpec
Memory. Offer the current working directory as the default. Wait for their
response before continuing.

## Step 5: Initialize the palace

Run `memory init --yes <dir>` where `<dir>` is the directory from Step 4. If
using the checkout launcher, run `python scripts/memory.py init --yes <dir>`.

If this fails, report the error and stop.

## Step 6: Configure MCP server

From a checkout, run:

    python scripts/memory.py mcp

Then run the printed `claude mcp add memory -- ...` or
`codex mcp add memory -- ...` command for the client the user is configuring.
The MCP server name is `memory`; tool identifiers remain
`wabblespec_memory_*` for client compatibility.

If this fails, report the error but continue to the next step. MCP
configuration can be done manually later.

## Step 7: Verify installation

Run `memory status` and confirm the output shows a healthy palace. If using the
checkout launcher, run `python scripts/memory.py status`.

If the command fails or reports errors, walk the user through troubleshooting
based on the output.

## Step 8: Show next steps

Tell the user setup is complete and suggest these next actions:

- Use /wabblespec_memory:mine to start adding data to their palace
- Use /wabblespec_memory:search to query their palace and retrieve stored knowledge
