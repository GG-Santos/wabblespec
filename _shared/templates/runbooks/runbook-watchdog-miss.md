# Runbook: Watchdog Miss

**Alert:** `WatchdogMiss`  
**Severity:** critical  
**SLO:** Watchdog feed interval ≤ ___ ms — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  
**Applies to:** IoT platform only  

---

## Symptoms

- Watchdog timer expired without being fed — device may have rebooted or is unresponsive
- Fleet monitoring shows device offline or unexpected reboot count increase
- `watchdog_feed_interval_ms` metric exceeding declared threshold
- Device has not reported telemetry for > ___ UNDECLARED seconds (stale-device threshold)
- For hardware watchdog: device reset event visible in boot log

---

## Immediate triage

1. Confirm whether device rebooted (watchdog-triggered reset) or is simply not feeding the watchdog without reset.
2. Check last known good telemetry timestamp for the affected device(s).
3. Is this a single device or a fleet-wide pattern (batch deploy, firmware update, shared environment condition)?
4. Check if a firmware OTA was recently pushed — new firmware may have introduced a blocking call in the watchdog feed path.
5. Check device power supply stability if available via hardware telemetry.

---

## Diagnosis

**Fleet query — devices with watchdog events:** `___ UNDECLARED` (insert fleet monitoring query)

**Device boot log:** `___ UNDECLARED` (insert log retrieval for affected device)

**Watchdog feed trace:** `___ UNDECLARED` (identify which task/thread is responsible for feeding watchdog and whether it is blocking)

**Common causes:**
- Blocking call in main loop (I2C/SPI timeout, filesystem operation stall)
- RTOS task priority inversion — watchdog feed task starved by higher-priority task
- Infinite loop or deadlock introduced in new firmware
- Interrupt storm consuming all CPU time
- Memory corruption corrupting task control block
- Power brown-out causing undefined behavior before full reset

---

## Remediation

1. If firmware OTA recently deployed: push rollback firmware via OTA to affected devices — `___ UNDECLARED`.
2. If blocking call identified: replace blocking call with timeout-bounded version; ensure watchdog feed is in a dedicated high-priority task or interrupt, not in the main application loop.
3. If RTOS priority issue: audit task priorities in `___ UNDECLARED`; watchdog feed task should be highest priority with minimal work.
4. If interrupt storm: add interrupt rate limiting in `___ UNDECLARED`; identify interrupt source via hardware counter registers.
5. If fleet-wide and cause unknown: pause further OTA rollouts until root cause identified.

**Prevention — required in build-toolchain:**
- Watchdog coverage check in CI (see `engineering/build-toolchain.md` IoT template)
- Static analysis confirms watchdog feed is called on all code paths through main loop

---

## Escalation

- More than ___ UNDECLARED % of fleet affected: page ___ UNDECLARED immediately (production fleet incident)
- Devices in safety-critical application: page ___ UNDECLARED immediately regardless of count
- Cause unknown after ___ UNDECLARED min: escalate to ___ UNDECLARED (firmware engineering lead)

---

## Post-incident

- [ ] Root cause identified (blocking call / priority / new firmware / power)
- [ ] Watchdog feed path verified non-blocking post-fix
- [ ] CI watchdog coverage check updated to catch regression
- [ ] OTA deploy policy reviewed (staged rollout gate added if not present)
- [ ] Runbook updated with device-specific diagnosis steps

---

*Generated from `_shared/templates/runbooks/runbook-watchdog-miss.md`. Replace all `___ UNDECLARED` with project-specific values before production use.*
