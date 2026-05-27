# Game AI Architecture Template

> **Platform:** Game | **Conditional load:** activate if AI enemies, NPCs, or autonomous agents are declared in game-concept.md or systems-index.md.
> **Prerequisites:** performance-budgets.md (AI budget declared), systems-design.md (physics/pathfinding declared).
> AI is a frame budget consumer. Architecture decisions here directly constrain Gate 13 compliance.

---

## AI Agent Registry [REQUIRED]

One row per distinct agent class. Each agent class gets its own budget and architecture declaration.

| Agent Class | Topology | Max simultaneous | Per-agent ms budget | Total budget | Pathfinding? |
|---|---|---|---|---|---|
| [PlayerEnemy] | BT / FSM / Utility / GOAP | ___ | ___ms | ___ms | Yes / No |
| [PassiveNPC] | FSM | ___ | ___ms | ___ms | No |

**Total AI budget check:** Sum of (max_simultaneous × per_agent_budget) for all agent classes must be ≤ declared AI budget in `performance-budgets.md`.

---

## Topology Selection [REQUIRED per agent class]

Choose one primary topology per agent class. Declare the rationale. Do not mix topologies within a single agent — it creates unpredictable priority resolution.

| Topology | Best for | Avoid when |
|---|---|---|
| **Finite State Machine (FSM)** | Simple agents with ≤8 states, fast to implement | States grow beyond ~10 (transition graph becomes unmaintainable) |
| **Behavior Tree (BT)** | Complex agents needing modular, reusable behaviors; designers must edit | Single-state agents (overhead without benefit) |
| **Utility AI** | Agents with many competing goals, no clear priority order | Tight frame budgets (scoring is expensive) |
| **GOAP** | Agents that need to plan multi-step action sequences | Real-time action games (planning latency is high) |

---

## Finite State Machine Declaration

*Complete this section if any agent uses FSM topology.*

```
Agent class: [Name]
States:
  IDLE      → entry: stop movement, play idle anim
              → exit: on DETECT_PLAYER or PATROL_TIMER
  PATROL    → entry: select next waypoint
              → exit: on DETECT_PLAYER or REACHED_WAYPOINT (→ IDLE)
  CHASE     → entry: set player as nav target
              → exit: on LOST_PLAYER (→ SEARCH) or IN_ATTACK_RANGE (→ ATTACK)
  ATTACK    → entry: trigger attack animation
              → exit: on ATTACK_COMPLETE (→ CHASE) or HEALTH_LOW (→ FLEE)
  SEARCH    → entry: move to last known player position
              → exit: on DETECT_PLAYER (→ CHASE) or SEARCH_TIMEOUT (→ PATROL)
  FLEE      → entry: move away from player
              → exit: on SAFE_DISTANCE_REACHED (→ IDLE)
  DEAD      → entry: play death anim, disable collisions
              → exit: never (terminal state)
```

**Transition table:**

| From | Trigger | To |
|---|---|---|
| IDLE | Player within detection range | CHASE |
| PATROL | Player within detection range | CHASE |
| CHASE | Lost sight for > Ns | SEARCH |
| CHASE | Within attack range | ATTACK |
| ATTACK | Health < threshold% | FLEE |
| SEARCH | Search timer expired | PATROL |

---

## Behavior Tree Declaration

*Complete this section if any agent uses BT topology.*

**Tick rate:** ___ Hz (not every frame — AI at 10Hz saves 5× tick cost vs 60Hz with minimal quality loss for most game types)

**Root structure:**

```
Root (Selector)
  ├── [Priority 1] Flee Sequence (Sequence)
  │     ├── Condition: Health < 20%
  │     └── Action: MoveToSafePosition
  ├── [Priority 2] Attack Sequence (Sequence)
  │     ├── Condition: TargetInAttackRange
  │     └── Action: PerformAttack
  ├── [Priority 3] Chase Sequence (Sequence)
  │     ├── Condition: TargetVisible
  │     └── Action: MoveToTarget
  └── [Priority 4] Patrol Fallback (Sequence)
        └── Action: PatrolWaypoints
```

**Node library — declare which node types are in use:**

| Node | Type | Description |
|---|---|---|
| `TargetInAttackRange` | Condition | True if player within attack_range units |
| `TargetVisible` | Condition | True if line-of-sight check passes |
| `MoveToTarget` | Action | Pathfind to current target position |
| `PerformAttack` | Action | Trigger attack, wait for animation, return Success |
| `PatrolWaypoints` | Action | Cycle through patrol point list |

**Max tree depth:** ___ nodes. Trees deeper than ~8 levels are hard to debug and slow to tick.

---

## Pathfinding Architecture [REQUIRED if any agent uses pathfinding]

**Navmesh strategy:**

| Property | Value |
|---|---|
| Navmesh type | Built-in engine / Recast/Detour / Custom |
| Agent radius | ___ units |
| Agent height | ___ units |
| Max slope angle | ___ degrees |
| Step height | ___ units |
| Recompute trigger | On position delta > ___ units from last query position |

**Dynamic obstacles:** [ ] Navmesh rebakes on obstacle change (expensive, use sparingly) [ ] Avoidance layer (RVO/ORCA — no rebake needed, lower quality) [ ] Static only (no dynamic obstacle support)

**Path query budget:** Max path queries per frame: ___. If demand exceeds budget, queries are queued and fulfilled over N frames.

**Pathfinding failure handling:**
```
If path not found:
  1. Retry with relaxed constraints (larger step height, ignore small obstacles)
  2. If still no path: enter SEARCH or IDLE state
  3. Log: agent_id, start position, target position, failure reason
  Never: loop infinite path queries when agent is stuck
```

---

## Difficulty Scaling [REQUIRED]

Declare which AI parameters scale with difficulty. Parameters not listed here do not scale.

| Parameter | Easy | Normal | Hard | Notes |
|---|---|---|---|---|
| Detection range | ___ units | ___ units | ___ units | |
| Reaction time | ___ms | ___ms | ___ms | Time from detect to first action |
| Attack damage | ___% | 100% | ___% | Relative to base |
| Patrol speed | ___ | ___ | ___ | |
| Accuracy (if ranged) | ___% | ___% | ___% | |

**Parameters that do NOT scale:** Pathfinding quality, animation timing, physics behavior. These affect feel, not challenge.

**Difficulty setting application:** Applied on session start, not mid-session unless explicitly designed (e.g., dynamic difficulty adjustment — declare separately).

---

## Performance Enforcement

**AI tick budget enforcement pattern:**

```
Per frame:
  1. Measure AI system tick start time
  2. Process agents in priority order (threat proximity to player)
  3. If elapsed > declared AI budget: defer remaining agents to next frame
  4. Low-priority agents (distant, idle) tick at reduced frequency (e.g., 5Hz instead of 10Hz)
  5. Log: if deferred count > 0 for > 3 consecutive frames, emit AI_BUDGET_BREACH warning
```

**LOD for AI (not just visual):** Distant agents use simplified FSM (IDLE / PATROL only). Full BT activates only when agent within ___ units of player.

---

## GWT Acceptance Scenarios

```
Given: an agent's pathfinding query returns no valid path
When: the pathfinding failure handler runs
Then: the agent transitions to SEARCH or IDLE (not loop-retry)
      AND the failure is logged with agent ID and target position
      AND no infinite loop or frame stall occurs

Given: maximum simultaneous agent count is active
When: the AI system tick is profiled over 5 minutes of gameplay
Then: p99 AI tick time ≤ declared per-agent budget × max_simultaneous
      AND no single frame exceeds 2× the declared AI budget

Given: difficulty is set to Hard
When: an agent detects the player
Then: reaction time ≤ declared Hard reaction time
      AND detection range ≥ declared Hard detection range
      AND damage per hit ≥ declared Hard damage multiplier × base damage

Given: an agent is more than [LOD threshold] units from the player
When: the AI tick runs for that agent
Then: the agent uses simplified FSM (not full BT)
      AND the simplified FSM tick cost is < 25% of full BT tick cost for that agent class

Given: a behavior tree action fails
When: the parent Sequence evaluates the failure
Then: the Sequence returns Failure to its parent
      AND the parent Selector tries the next child
      AND no unhandled exception propagates to the game loop
```

---

## Open Questions

Unresolved topology choices, unbudgeted agent classes, or undefined difficulty parameter values go here.
