# Memory Closets

Archived drawers land here. Format: `{drawer-id}-{YYYYMMDDTHHMMSS}.json`

Drawers are moved here when:
- staleness_state transitions to EXPIRED (via Memory transition path)
- staleness_state transitions to SUPERSEDED (old drawer archived when new one created)
- Forget module explicitly archives a drawer

Closet files are read-only after archiving. Do not edit them.
Provenance retains the deletion/archive record in `provenance/index.json`.
