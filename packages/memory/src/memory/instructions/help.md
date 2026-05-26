# WabbleSpec Memory

AI memory system. Store everything, find anything. Local, free, no API key.

---

## Slash Commands

| Command              | Description                    |
|----------------------|--------------------------------|
| /wabblespec_memory:init      | Install and set up WabbleSpec Memory   |
| /wabblespec_memory:search    | Search your memories           |
| /wabblespec_memory:mine      | Mine projects and conversations|
| /wabblespec_memory:status    | Palace overview and stats      |
| /wabblespec_memory:help      | This help message              |

---

## MCP Tools (19)

### Palace (read)
- wabblespec_memory_status -- Palace status and stats
- wabblespec_memory_list_wings -- List all wings
- wabblespec_memory_list_rooms -- List rooms in a wing
- wabblespec_memory_get_taxonomy -- Get the full taxonomy tree
- wabblespec_memory_search -- Search memories by query
- wabblespec_memory_check_duplicate -- Check if a memory already exists
- wabblespec_memory_get_aaak_spec -- Get the AAAK specification

### Palace (write)
- wabblespec_memory_add_drawer -- Add a new memory (drawer)
- wabblespec_memory_delete_drawer -- Delete a memory (drawer)

### Knowledge Graph
- wabblespec_memory_kg_query -- Query the knowledge graph
- wabblespec_memory_kg_add -- Add a knowledge graph entry
- wabblespec_memory_kg_invalidate -- Invalidate a knowledge graph entry
- wabblespec_memory_kg_timeline -- View knowledge graph timeline
- wabblespec_memory_kg_stats -- Knowledge graph statistics

### Navigation
- wabblespec_memory_traverse -- Traverse the palace structure
- wabblespec_memory_find_tunnels -- Find cross-wing connections
- wabblespec_memory_graph_stats -- Graph connectivity statistics

### Agent Diary
- wabblespec_memory_diary_write -- Write a diary entry
- wabblespec_memory_diary_read -- Read diary entries

---

## CLI Commands

    memory init <dir>                  Initialize a new palace
    memory mine <dir>                  Mine a project (default mode)
    memory mine <dir> --mode convos    Mine conversation exports
    memory search "query"              Search your memories
    memory split <dir>                 Split large transcript files
    memory wake-up                     Load palace into context
    memory compress                    Compress palace storage
    memory status                      Show palace status
    memory repair                      Rebuild vector index
    wabblespec_memory mcp                         Show MCP setup command
    memory hook run                    Run hook logic (for harness integration)
    memory instructions <name>         Output skill instructions

---

## Auto-Save Hooks

- Stop hook -- Automatically saves memories every 15 messages. Counts human
  messages in the session transcript (skipping command-messages). When the
  threshold is reached, blocks the AI with a save instruction. Uses
  ~/.wabblespec_memory/hook_state/ to track save points per session. If
  stop_hook_active is true, passes through to prevent infinite loops.

- PreCompact hook -- Emergency save before context compaction. Always blocks
  with a comprehensive save instruction because compaction means the AI is
  about to lose detailed context.

Hooks read JSON from stdin and output JSON to stdout. They can be invoked via:

    echo '{"session_id":"abc","stop_hook_active":false,"transcript_path":"..."}' | memory hook run --hook stop --harness claude-code

---

## Architecture

    Wings (projects/people)
      +-- Rooms (topics)
            +-- Closets (summaries)
                  +-- Drawers (verbatim memories)

    Halls connect rooms within a wing.
    Tunnels connect rooms across wings.

The palace is stored locally using ChromaDB for vector search and SQLite for
metadata. No cloud services or API keys required.

---

## Getting Started

1. /wabblespec_memory:init -- Set up your palace
2. /wabblespec_memory:mine -- Mine a project or conversation
3. /wabblespec_memory:search -- Find what you stored
