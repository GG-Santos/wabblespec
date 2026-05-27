# Platform IoT/Embedded — Acceptance Criteria

## BLOCK: Recipe not run first

Given Recipe has not run and identified IoT/Embedded as the primary target,
When platform-iot is invoked,
Then it surfaces: "platform-iot requires Recipe to have identified IoT/Embedded as the primary target first."
Then no platform activation receipt is written.

## Happy path: activation sequence

Given Recipe has identified IoT/Embedded as the primary target,
When platform-iot activates,
Then the activation sequence completes in order: toolchain detection → spec-template load → engineering load → security load → Verifier gate registration → receipt write.

## IoT/Embedded-specific concerns injected into spec

Given platform-iot is active,
When spec context is assembled,
Then flash size gate is declared: the spec must declare the flash budget and that code must fit.
Then RAM budget is declared: stack overflow at runtime is the failure mode for exceeded RAM.
Then watchdog timer is declared: stuck code must recover automatically.
Then signed OTA update is declared: firmware updates are an attack vector; unsigned OTA is BLOCK.
Then fail-safe behavior is declared: behavior on power loss mid-write is specified.
Then hardware abstraction layer design is addressed.
Then secure boot declaration is required.

## Real-time deadlines declared

Given the spec includes any real-time operations,
When spec context is assembled,
Then hard deadline requirements are declared.
Then the spec acknowledges that a missed real-time deadline is a system failure — not a soft warning.

## No virtual memory: RAM ceiling is absolute

Given platform-iot is active,
When spec context is assembled,
Then the spec acknowledges that there is no virtual memory paging on the target device.
Then all allocations must fit within the declared RAM budget.
Then dynamic allocation is either prohibited in the hot path or accounted for in the budget.

## Signed OTA required

Given the spec includes an OTA update mechanism,
When spec context is assembled,
Then the OTA update process requires cryptographic signature verification before applying.
Then rollback is declared: a failed OTA must roll back to the last known-good firmware.

## Debug tooling declared

Given platform-iot is active,
When spec context is assembled,
Then debug tooling is declared: JTAG/SWD for hardware debugging, UART for log output.
Then the spec does not assume browser DevTools or GUI debuggers are available.

## Testing requires hardware or emulator

Given platform-iot is active,
When spec context is assembled,
Then the spec declares the testing method: hardware target or hardware emulator.
Then x86 unit tests are not the only test method for hardware-specific behavior.

## Missing rules files fallback

Given `verification/gates.md` is absent,
When platform-iot attempts gate registration,
Then it logs: "verification/gates.md absent — Verifier registration skipped."
Then activation proceeds with a warning in the receipt.

## Do NOT

Given any platform-iot run,
Then platform-iot does not allow unsigned OTA firmware updates.
Then platform-iot does not omit flash and RAM budget declarations.
Then platform-iot does not treat IoT as equivalent to a Web or Desktop target.

## Receipt fields

Given any successful platform-iot activation,
Then a receipt is written to `.wabblespec/receipts/platform-iot-<timestamp>.json`.
Then the receipt contains: platform, toolchain_detected, flash_budget_declared, ram_budget_declared, watchdog_declared, signed_ota_declared, fail_safe_declared, gates_registered, capability_handoff.
