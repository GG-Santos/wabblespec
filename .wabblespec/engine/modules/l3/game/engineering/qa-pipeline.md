# Game Engineering — QA Pipeline

> This document covers how to build and run the QA pipeline for game projects. The verification gates (`verification/gates.md`) declare what must pass. This document declares how to set up the infrastructure to run those gates.

---

## Test Classification

Every test in the project is assigned to exactly one type. Type determines: automation potential, where it runs, and what counts as passing evidence.

| Type | Automation | Runs in CI | Evidence |
|---|---|---|---|
| **Logic** | Required | Yes | Unit test passes, deterministic |
| **Integration** | Required | Yes | Integration test passes in test env |
| **Visual / Feel** | Not possible | No | Playtest record (see evidence format) |
| **Config / Data** | Required (schema) | Yes | JSON schema validation passes |
| **Performance** | Required | Yes (on target hardware) | Profiler output within declared budget |

**Logic tests** cover: state machines, damage formulas, economy transactions, save/load serialization, pathfinding result correctness.

**Integration tests** cover: system A + system B interaction (player takes damage → health bar updates), multiplayer input → server state roundtrip, save → corrupt → load → recovery.

**Visual / Feel tests** are playtests. They are not automatable. Every Visual/Feel test must produce a written evidence record.

**Config / Data tests** cover: JSON item tables, loot weights, level config files. Schema validation catches malformed data before it reaches the game.

---

## Engine-Specific Test Scaffolding

### Unity — Unity Test Framework

```csharp
// Logic test (runs in Edit Mode — no game loop needed)
[TestFixture]
public class HealthSystemTests
{
    [Test]
    public void TakeDamage_ReducesHealthByAmount()
    {
        var health = new HealthComponent(maxHealth: 100);
        health.TakeDamage(30);
        Assert.AreEqual(70, health.Current);
    }

    [Test]
    public void TakeDamage_CannotGoBelowZero()
    {
        var health = new HealthComponent(maxHealth: 100);
        health.TakeDamage(150);
        Assert.AreEqual(0, health.Current);
    }
}

// Integration test (runs in Play Mode — full game loop active)
[UnityTestFixture]
public class SaveLoadIntegrationTests
{
    [UnityTest]
    public IEnumerator SaveLoad_RestoresPlayerPosition()
    {
        var player = SpawnPlayer(new Vector3(10, 0, 5));
        SaveManager.Save(slot: 0);
        player.transform.position = Vector3.zero;  // move away
        SaveManager.Load(slot: 0);
        yield return null;  // wait one frame for load to complete
        Assert.AreApproximatelyEqual(10f, player.transform.position.x, delta: 0.01f);
    }
}

// Performance test — Unity Performance Testing Package
[Performance, UnityTest]
public IEnumerator BenchmarkCombatScene_MeetsFrameBudget()
{
    SceneManager.LoadScene("CombatBenchmark");
    yield return null;
    using (Measure.Frames().WarmupCount(10).MeasurementCount(100).Run())
    {
        yield return null;
    }
    // Assertion: median frame time reported in Performance Test Framework results
    // Check against 16.6ms manually or via custom PerformanceTestHelper.AssertMedian(16.6f)
}
```

**Test assembly setup:** Create `Tests.asmdef` (Edit Mode) and `Tests.Runtime.asmdef` (Play Mode) in `Assets/Tests/`. Reference only the assemblies under test — not all game assemblies.

**CI integration:** `unity-test-runner` GitHub Action (or equivalent). Runs Edit Mode + Play Mode tests on every PR. Play Mode tests require headless Unity license.

---

### Godot — GUT (Godot Unit Test)

```gdscript
# Install: Godot Unit Test (GUT) from Asset Library or github.com/bitwes/Gut
# File naming: test_*.gd in res://tests/

# test_health_system.gd
extends GutTest

var _health: HealthComponent

func before_each() -> void:
    _health = HealthComponent.new()
    _health.max_health = 100
    _health.reset()

func test_take_damage_reduces_health() -> void:
    _health.take_damage(30)
    assert_eq(_health.current, 70, "Health should be 70 after 30 damage")

func test_take_damage_cannot_go_below_zero() -> void:
    _health.take_damage(150)
    assert_eq(_health.current, 0, "Health should not go below 0")

# Async test (for coroutine-based logic)
func test_death_sequence_completes() -> void:
    var enemy: Enemy = ENEMY_SCENE.instantiate()
    add_child(enemy)
    enemy.die()
    await wait_seconds(2.5)  # wait for death animation + timer
    assert_false(is_instance_valid(enemy), "Enemy node should be freed after death sequence")
```

**Running tests:**
```bash
# Headless (CI):
godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests/ -gexit

# With output:
godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests/ -glog=3 -gexit
```

**Naming convention:** Test files `test_[system_name].gd`. Test functions `test_[behavior_under_test]`. One assertion per test function where possible.

---

### Unreal — Automation Framework

```cpp
// Logic test
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FHealthComponentTest,
    "Game.Combat.HealthComponent.TakeDamageReducesHealth",
    EAutomationTestFlags::ApplicationContextMask | EAutomationTestFlags::ProductFilter
)

bool FHealthComponentTest::RunTest(const FString& Parameters)
{
    UHealthComponent* Health = NewObject<UHealthComponent>();
    Health->MaxHealth = 100.f;
    Health->CurrentHealth = 100.f;

    Health->TakeDamage(30.f);
    TestEqual("Health after 30 damage", Health->CurrentHealth, 70.f);

    Health->TakeDamage(150.f);
    TestEqual("Health cannot go below zero", Health->CurrentHealth, 0.f);

    return true;
}

// Latent (async) test — for anything requiring ticks
DEFINE_LATENT_AUTOMATION_COMMAND_ONE_PARAMETER(FWaitForSaveLoad, float, WaitSeconds);
bool FWaitForSaveLoad::Update()
{
    // Returns true when done waiting
    return FPlatformTime::Seconds() - StartTime >= WaitSeconds;
}
```

**Running via CLI:**
```bash
# Run all tests matching filter
UnrealEditor-Cmd.exe MyGame.uproject -ExecCmds="Automation RunTests Game.Combat" -Unattended -NullRHI -log

# Run all tests
UnrealEditor-Cmd.exe MyGame.uproject -ExecCmds="Automation RunAll" -Unattended -NullRHI -log
```

---

## Smoke Test Protocol

The smoke test is the minimum test that runs before any playtest build or QA handoff. It must complete in ≤ 10 minutes.

**Critical path:**
1. Game launches to main menu — no crash, no error dialog
2. New game starts — loading screen appears, level loads
3. Player spawns — character visible, movement inputs respond
4. One core interaction completes (attack connects, item collected, dialogue triggers — declare which)
5. Pause menu opens and resumes
6. Game exits cleanly (no hang on quit)

**Smoke test result:** PASS (all 6 steps complete without error) or FAIL (any step fails — build does not proceed to QA).

**Automation target:** Steps 1–2, 5–6 are automatable. Steps 3–4 are run by a human and logged in a smoke test evidence record.

---

## Regression Suite Strategy

Every fixed bug produces one test that would have caught it. No exceptions.

**Naming:** Test file named after bug ID: `test_bug_[ID]_[short_description].gd` / `[Engine]Test_Bug[ID].cpp`.

**Regression test structure:**
```
1. Set up the exact precondition that caused the bug
2. Execute the action that triggered the bug
3. Assert the correct behavior (post-fix)
```

**Regression test ownership:** The developer who fixes the bug writes the test. The QA lead verifies the test would have caught the bug before the fix is merged.

**Suite maintenance:** Regression tests are never deleted. If a test becomes obsolete due to feature removal, it is marked `[SKIP]` with a reason, not deleted.

---

## Soak Test Protocol (Gate 9)

Gate 9 requires 1 hour of continuous play with zero crashes. This is the full protocol.

**Setup:**
1. Use Release/Shipping build, not Debug (debug builds allocate differently and mask leaks)
2. Start memory profiler before launch
3. Record: start RSS, start time

**Script:**
```
Minutes 0–10:  Play through opening sequence, reach first major area
Minutes 10–25: Traverse all accessible areas, trigger all enemy types
Minutes 25–35: Heavy spawn/despawn: enter area, kill all enemies, exit, repeat 3×
Minutes 35–45: Open and close inventory/menus 20× each; trigger all UI screens
Minutes 45–55: Trigger save/load 5× (save, continue, load different slot, continue)
Minutes 55–60: Return to starting area; idle for 5 minutes (audio, ambient effects)
```

**Metrics to record:**
- RSS memory at 0, 15, 30, 45, 60 minutes
- Crash count (must be 0)
- Frame time anomalies (any frame > 50ms, logged with timestamp and scene)
- Any error/warning logged to console during session

**Pass criteria:** Zero crashes, zero hangs. RSS at 60 min − RSS at 0 min ≤ 50MB. No frame > 50ms lasting > 3 consecutive frames.

---

## Manual Test Evidence Format

For Visual/Feel tests that cannot be automated. One record per test.

```
Test ID:       [manual-001]
Type:          Visual / Feel
Test name:     [Player death animation feels impactful]
Tester:        [Name]
Date:          [YYYY-MM-DD]
Build:         [version/commit]
Platform:      [PC Win64 / iOS / etc.]

Precondition:  [Player at full health in combat area]
Steps:
  1. [Step]
  2. [Step]
Expected:      [What correct behavior looks like]
Actual:        [What was observed]
Result:        PASS / FAIL / NEEDS REVISION

Notes:         [Any relevant observations]
Evidence:      [Screenshot path or video timestamp]
```

Completed evidence records are stored in `tests/evidence/manual/`. They are version-controlled. Gate sign-off requires evidence records for all declared Visual/Feel tests.

---

## CI Pipeline Gates (per engine)

Before any build reaches QA:

| Step | Unity | Godot | Unreal | Blocking |
|---|---|---|---|---|
| Compile | Unity -batchmode | `godot --headless --export` | UBT build | Yes |
| Logic tests | Unity Test Framework (Edit Mode) | GUT headless | Automation RunTests | Yes |
| Integration tests | Unity Test Framework (Play Mode) | GUT with scene | Automation RunTests (latent) | Yes |
| Data schema validation | Custom script on Assets/Data/ | Custom script on res://data/ | Custom script on Content/Data/ | Yes |
| Build size check | Compare output vs declared budget | Compare output vs declared budget | Compare output vs declared budget | Yes |
| Smoke test | Automated (launch + menu) + manual steps | Automated + manual | Automated + manual | Yes |
