# Runbook: Flash Threshold Breach

**Alert:** `FlashThresholdBreach`  
**Severity:** warning (> declared ceiling) | critical (> 95% capacity)  
**SLO:** Flash utilization ≤ ___ % of device flash — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  
**Applies to:** IoT platform only  

---

## Symptoms

- Static analysis CI gate reporting flash usage exceeds declared budget (build-time alert)
- Fleet monitoring showing flash utilization above threshold on deployed devices
- Firmware build size (`___ UNDECLARED` bytes) exceeds declared ceiling
- OTA update failing because insufficient flash space to stage update image
- For littlefs/SPIFFS: filesystem full errors in device logs

---

## Immediate triage

1. Distinguish: is this a firmware binary size issue (build-time) or a filesystem/data storage issue (runtime)?
2. **Build-time:** Which component added to the binary in the last change? Compare map file against previous build.
3. **Runtime:** Which partition is full — firmware, filesystem, or NVS/EEPROM?
4. If OTA blocked by insufficient space: what is the free flash vs. update image size?
5. Is this a single device anomaly (corrupted filesystem) or fleet-wide (new firmware too large)?

---

## Diagnosis

**Build-time — map file analysis:**
```
# Compare section sizes between builds
___ UNDECLARED  # insert your linker map diff command
```

**Build-time — top contributors to binary size:**
```
___ UNDECLARED  # insert bloaty / size-report invocation
```

**Runtime — flash partition table:** `___ UNDECLARED` (insert command to query partition layout and free space on device)

**Runtime — filesystem usage:** `___ UNDECLARED` (insert NVS / SPIFFS / littlefs stats query)

**Common causes (firmware binary size):**
- New dependency added without evaluating size impact
- Debug symbols or logging left enabled in release build
- String table bloat (verbose error messages, log strings)
- Unused code not eliminated (LTO not enabled or function pointers defeating dead-code elimination)
- Third-party library not size-optimized for embedded target

**Common causes (runtime filesystem):**
- Log rotation not implemented — device log files growing unbounded
- Cached data not purged on expiry
- OTA staging partition not cleared after successful update
- Corrupted filesystem causing apparent full state (actual space available but inaccessible)

---

## Remediation

### Build-time binary size
1. Enable LTO (Link Time Optimization) in `___ UNDECLARED` build config if not already active.
2. Replace verbose string literals with error codes + lookup table.
3. Identify the largest new contributor from the map diff and reduce or replace.
4. Set linker script floor: linker fails build if flash exceeds budget — `___ UNDECLARED`.
5. If third-party lib is the cause: find a size-optimized alternative or vendor only the required subset.

### Runtime filesystem full
1. If log files: enable log rotation in `___ UNDECLARED` config with max size `___ UNDECLARED` KB and retention `___ UNDECLARED` files.
2. If stale OTA staging: clear staging partition via `___ UNDECLARED` command.
3. If corrupted filesystem: format and restore from known-good state; investigate corruption cause (power-loss during write — enable journaling or atomic writes).
4. If NVS/EEPROM fragmentation: run NVS compaction or migrate to fresh namespace.

### OTA blocked
1. Clear staging partition first, then retry OTA.
2. If firmware binary itself is too large for available slot: build with size optimizations, then push delta OTA if supported.

---

## Escalation

- Flash > 95%: page ___ UNDECLARED — device may fail to accept next OTA update
- Build-time flash ceiling exceeded and no quick fix: escalate to ___ UNDECLARED (firmware architect) for architecture review
- Corrupted filesystem on > ___ UNDECLARED % of fleet: page ___ UNDECLARED immediately

---

## Post-incident

- [ ] Root cause documented (binary bloat / filesystem / OTA staging)
- [ ] Flash budget ceiling enforced in linker script and CI gate
- [ ] Log rotation configured on all deployed devices
- [ ] Map file size tracking added to CI dashboard if not already present
- [ ] Runbook updated with device-specific partition layout

---

*Generated from `_shared/templates/runbooks/runbook-flash-threshold-breach.md`. Replace all `___ UNDECLARED` with project-specific values before production use.*
