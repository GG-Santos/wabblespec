# Game Verification Gates

Registered with Verifier at platform activation. All gates must pass before Delivery wave.

---

## Gate 1: Frame Rate Target Met

**Check:** Game runs at declared target fps on minimum spec hardware.

**Method:** Run benchmark scene for 5 minutes. Record frame times. p50 ≤ frame budget. p99 ≤ 2× frame budget.

**Pass:** Median frame time within budget on minimum spec. No sustained hitching. **Fail:** Median exceeds budget or p99 > 2× budget.

---

## Gate 2: Memory Within Budget

**Check:** RSS memory within declared budget after 30-minute session.

**Method:** Profile 30-minute session (spawn/despawn, travel between areas). Measure RSS at start and end. Difference ≤ 50MB (no leak).

**Pass:** Memory within budget. No unbounded growth. **Fail:** Exceeds budget or grows monotonically.

---

## Gate 3: Save/Load Integrity

**Check:** Save → corrupt → load recovers from backup. Save → load restores exact state.

**Method:**
1. Save at known state
2. Corrupt save bytes
3. Load → verify backup loaded, player notified
4. Save again → load → verify exact state match

**Pass:** Corruption detected, backup loaded, state restored. **Fail:** Corrupt save causes crash or wrong state loaded.

---

## Gate 4: Load Time Within Budget

**Check:** Scene loads within declared budget.

**Method:** Time from load trigger to game interactive. Minimum spec hardware.

**Pass:** Within declared budget. **Fail:** Exceeds budget.

---

## Gate 5: Server Input Validation (Multiplayer)

**Check:** Server rejects invalid inputs from clients.

**Method:** Automated test client sends: speed-hack position, impossible action, duplicate timestamp.

**Pass:** All invalid inputs rejected. Server state unaffected. Client corrected. **Fail:** Any invalid input applied to server state.

---

## Gate 6: Anti-Cheat Scope Matches Declaration

**Check:** Anti-cheat implementation matches declared scope in design-document.md.

**Method:** If `server-authoritative` declared: verify server validates all inputs per Control 2. If `none-singleplayer` declared: verify no false claims of competitive integrity.

**Pass:** Implementation matches declaration. **Fail:** Mismatch between declared scope and actual implementation.

---

## Gate 7: Platform Certification Checklist Started

**Check:** For console targets, certification checklist reviewed and blocking items addressed.

**Method:** Download platform-specific TRC/XR/Lot Check document. Review required features. Document: compliant / not applicable / needs work.

**Pass:** All required features either implemented or explicitly not applicable. **Fail:** Any certification-required feature unaddressed.

---

## Gate 8: Build Size Within Budget

**Check:** Distribution build size within declared budget for all target platforms.

**Method:** Measure compressed download size of release build for each platform.

**Pass:** All platforms within declared budget. **Fail:** Any platform exceeds declared budget.

---

## Gate 9: No Crash in 1-Hour Soak Test

**Check:** Game runs for 1 hour without crash, hang, or out-of-memory error.

**Method:** Automated or manual: run game for 1 hour, traverse all major areas, spawn/despawn heavily.

**Pass:** Zero crashes, hangs, or OOM events. **Fail:** Any crash or hang.

---

---

## Gate 10: Engine Version Declared and Deprecated API Check

**Check:** The engine name and version are declared in `technical-spec.md`. Deprecated APIs for the declared version are not present in source.

**Why this gate exists:** LLM training data has a cutoff date. Game engines (Unity, Godot, Unreal) ship breaking changes and deprecate APIs between versions. Without a version declaration and deprecated-API check, generated code may reference patterns that are removed, renamed, or actively harmful in the declared engine version.

**Method — version declaration:**
```bash
# Confirm technical-spec.md declares engine name and version
grep -i 'engine\|unity\|godot\|unreal' modules/l3/game/spec-template/technical-spec.md
# Or in the project's technical-spec artifact:
grep -iE 'engine.*version|unity [0-9]|godot [0-9]|unreal [0-9]' technical-spec.md
```

**Method — deprecated API scan (engine-specific):**

Run the check matching the declared engine. Each engine has known deprecated patterns that generate warnings or compile errors in current versions.

Unity — common deprecated patterns to grep:
```bash
grep -rn \
  -e 'FindObjectOfType\b' \
  -e 'Resources\.Load\b' \
  -e 'using UnityEngine\.Networking' \
  -e 'UnityEngine\.UI\.' \
  -e 'OnGUI()' \
  Assets/Scripts/ --include="*.cs"
# Each match: review against declared version's deprecated-apis list
```

Godot — common deprecated patterns:
```bash
grep -rn \
  -e '\.connect("' \
  -e 'yield(' \
  -e '\.instance()' \
  -e 'OS\.get_ticks_msec\b' \
  . --include="*.gd"
```

Unreal — common deprecated patterns:
```bash
grep -rn \
  -e 'DEPRECATED\b' \
  -e 'UE_DEPRECATED\b' \
  -e '// Deprecated' \
  Source/ --include="*.cpp" --include="*.h"
```

**Pass:** Engine name and major version declared in technical-spec.md. Zero unreviewed deprecated API matches (each match either fixed or documented as accepted with engine-version rationale).

**Fail:** No engine version declared. Or: deprecated API matches present without documented review.

**Engine reference maintenance policy:**

When the project upgrades engine version, before the first wave using the new version:
1. Update the engine version declaration in technical-spec.md
2. Review the new version's breaking-changes and deprecated-apis against current source
3. Gate 10 re-runs; any newly deprecated patterns become Gate 10 findings

This is the same trigger as the engine-reference maintenance policy: engine upgrade → reference update → deprecated API re-check.

**Applies to:** All game targets with any declared engine. SKIP only if project is purely custom-engine with no third-party engine dependency.

---

## Gate 11: Accessibility Minimum Compliance

**Applies to:** All games with any UI. Required for console certification (Sony, Microsoft). Required for any game with voiced dialogue (subtitles).

**Check:** The four minimum accessibility features are present and functional.

**Method:**
1. Open accessibility / settings menu. Verify colorblind mode option exists (deuteranopia at minimum). Activate it. Play through first 5 minutes. Confirm all critical information (health, enemies, pickups) is distinguishable.
2. Navigate to remapping settings. Remap all declared gameplay actions (not presets only). Confirm remapped inputs work in gameplay.
3. Increase text scaling to 150%. Confirm all UI text scales without overlap or truncation.
4. Enable subtitles. Trigger any voiced dialogue. Confirm subtitle appears with speaker name (if off-screen) within 0.5 seconds of audio start.

**Pass:** All four features present, functional, and non-breaking at the declared accessibility tier. Features declared "N/A" in `ui-spec.md` are skipped for this gate.

**Fail:** Any declared feature absent or non-functional. Subtitle text overflows screen at 150% scaling. Remapping causes input conflicts.

**Console note:** Sony PS5 accessibility requirements and Microsoft Xbox Accessibility Guidelines (XBAG) each have specific feature lists. Gate 11 covers the common baseline. Platform-specific requirements are audited in Gate 7 (certification checklist).

---

## Gate 12: Content Completeness

**Applies to:** All games where `design-document.md` content inventory section declares MVP counts for any category.

**Check:** Implemented content count ≥ declared MVP count for every content category listed in the content inventory.

**Method — count per category:**
```bash
# Levels (Unity — count scene files)
find Assets/Scenes/Levels -name "*.unity" | wc -l

# Levels (Godot — count scene files)
find scenes/levels -name "*.tscn" | wc -l

# Enemy types (count prefabs/scenes in enemy directory)
# Item types (count rows in item data file)
# Dialogue lines (count entries in dialogue database)
# — Adapt paths to project structure declared in directory-structure.md
```

Compare each count against the MVP column in `design-document.md` content inventory.

**Pass:** All MVP-tier counts met (≥ 100% of declared). Any count at 80–99% of MVP: CONCERNS (surface to user — declare which category and gap). Any count below 80%: FAIL.

**Fail:** Any MVP-tier content category below 80% of declared count.

**Note:** This gate does not check Vertical Slice, Alpha, or Full Vision counts — only MVP. Gate runs once before Delivery wave. Does not re-run on non-MVP tier targets unless explicitly triggered.

---

## Gate 13: AI Performance Under Load

**Applies to:** All games with AI agents declared in `spec-template/ai-architecture.md`. Skip if no AI agents are declared.

**Check:** Total AI system tick time ≤ declared AI budget from `engineering/performance-budgets.md` at maximum declared simultaneous agent count.

**Method:**
1. Load or construct a benchmark scene with the maximum declared simultaneous agent count for each agent class.
2. Run the scene for 5 minutes with all agents active (patrolling, detecting, attacking — full behavior active, not idle-only).
3. Profile the AI system tick in isolation using engine profiler:
   - Unity: Profile → CPU Usage → filter by AI scripts
   - Godot: Profiler → Script functions → filter by AI node scripts
   - Unreal: Unreal Insights → CPU track → filter by BehaviorTree / NavMesh threads
4. Record: median AI tick time, p99 AI tick time.

**Pass:** p99 AI tick ≤ declared AI budget. No sustained breach (> 3 consecutive frames over budget).

**Fail:** p99 AI tick exceeds declared budget. Or: any single frame AI tick > 2× declared budget.

**Root cause guidance:** If gate fails, isolate by agent class: disable one class at a time and re-profile. Common causes: BT ticking every frame instead of at declared Hz, pathfinding queries not throttled, AI spawned above declared maximum.

---

## Gate Summary

| Gate | Description | Blocking | Condition |
|---|---|---|---|
| 1 | Frame rate target met | Yes | Always |
| 2 | Memory within budget | Yes | Always |
| 3 | Save/load integrity | Yes | Always |
| 4 | Load time within budget | Yes | Always |
| 5 | Server input validation | Yes | Multiplayer only |
| 6 | Anti-cheat scope matches declaration | Yes | Always |
| 7 | Platform certification checklist | Yes | Console targets only |
| 8 | Build size within budget | Yes | Always |
| 9 | 1-hour soak test — no crash | Yes | Always |
| 10 | Engine version declared + deprecated API check | Yes | Any declared engine |
| 11 | Accessibility minimum compliance | Yes | Any UI present; console required |
| 12 | Content completeness | Yes | Content inventory declared in design-document.md |
| 13 | AI performance under load | Yes | AI agents declared in ai-architecture.md |

All applicable gates are blocking. No Delivery wave proceeds with any applicable gate in FAIL state. Gates whose condition is not met for this project are skipped — document the skip reason in the platform activation receipt.
