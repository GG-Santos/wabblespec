# Platform Game — Acceptance Criteria

## BLOCK: Recipe not run first

Given Recipe has not run and identified Game as the primary target,
When platform-game is invoked,
Then it surfaces: "platform-game requires Recipe to have identified Game as the primary target first."
Then no platform activation receipt is written.

## Happy path: activation sequence

Given Recipe has identified Game as the primary target,
When platform-game activates,
Then the activation sequence completes in order: engine detection → spec-template load → engineering load → security load → Verifier gate registration → receipt write.

## Engine routing: Unity

Given `Assets/` directory and `.unity` scene files are detected,
When platform-game detects the engine,
Then `.wabblespec/engine/shared/dev/frameworks/game/unity.md` is loaded.

## Engine routing: Unreal

Given `Source/` directory and `.uproject` file are detected,
When platform-game detects the engine,
Then `.wabblespec/engine/shared/dev/frameworks/game/unreal.md` is loaded.

## Engine routing: Godot

Given `project.godot` is detected,
When platform-game detects the engine,
Then `.wabblespec/engine/shared/dev/frameworks/game/godot.md` is loaded.

## Engine routing: web game

Given `index.html` with a canvas element and a game loop is detected,
When platform-game detects the engine,
Then web game context is activated.
Then no native engine framework is loaded.

## Game-specific concerns injected into spec

Given platform-game is active,
When spec context is assembled,
Then frame budget is declared: 16.6ms (60fps) or 11.1ms (90fps).
Then the update loop architecture is declared: fixed timestep for physics, variable render.
Then asset pipeline is addressed: textures, meshes, audio compressed and streamed.
Then memory strategy is addressed: pool allocators, no GC pauses in the hot path.
Then save system integrity is declared: corrupt save = catastrophic UX failure.

## Server authority declared for multiplayer

Given the spec includes multiplayer or networked gameplay,
When spec context is assembled,
Then server authority is declared: client-side-only validation is not acceptable.
Then client prediction and rollback strategy is addressed.
Then anti-cheat architecture scope is declared.

## Platform certification scope declared

Given the spec targets a console platform (Sony/Microsoft/Nintendo),
When spec context is assembled,
Then the spec declares which certification requirements apply.
Then the spec notes that certification requirements must be verified before submission.

## Frame budget enforced in spec

Given platform-game is active,
When spec context is assembled,
Then the declared frame budget is referenced in performance gates.
Then exceeding the frame budget is a FAIL condition in Verifier gates.

## Missing rules files fallback

Given `verification/gates.md` is absent,
When platform-game attempts gate registration,
Then it logs: "verification/gates.md absent — Verifier registration skipped."
Then activation proceeds with a warning in the receipt.

## Do NOT

Given any platform-game run,
Then platform-game does not omit frame budget declaration.
Then platform-game does not allow client-side-only authority for multiplayer games.
Then platform-game does not treat a game target as equivalent to a Web or Desktop target.

## Receipt fields

Given any successful platform-game activation,
Then a receipt is written to `.wabblespec/state/receipts/platform-game-<timestamp>.json`.
Then the receipt contains: platform, engine_detected, frame_budget_declared, multiplayer_authority_declared, save_system_declared, platform_cert_scope, gates_registered, capability_handoff.
