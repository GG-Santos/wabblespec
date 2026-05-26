# Runbook: Memory Breach

**Alert:** `MemoryBreach` (or `MemoryUsageHigh`)  
**Severity:** warning (approaching limit) | critical (at/exceeding limit)  
**SLO:** Memory usage ≤ ___ MB / ≤ ___ % of container limit — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  

---

## Symptoms

- Memory usage metric approaching or exceeding declared budget
- Container / process memory reported above ___ % of declared limit
- For mobile: per-session memory footprint exceeding ___ MB
- For desktop: idle memory exceeding ___ MB declared in performance budgets
- For IoT: RAM utilization exceeding ___ % of device RAM
- Downstream signal: if memory is not released, system eventually crashes — see `runbook-crash-rate-breach.md`

---

## Immediate triage

1. Confirm memory is growing over time (leak pattern) vs. a one-time spike (expected load).
2. Check deployment log — was a deploy in the last 24h that changed memory allocation?
3. Check load level — is memory elevated because traffic is elevated (expected) or is it growing under constant load (leak)?
4. Check garbage collection / memory management logs for the runtime.
5. Is memory growing in all instances or only one?

---

## Diagnosis

**PromQL — memory trend (container):**
```
container_memory_working_set_bytes{container="___ UNDECLARED", namespace="___ UNDECLARED"}
/ 1024 / 1024   # convert to MB
```

**PromQL — memory as % of limit:**
```
container_memory_working_set_bytes{container="___ UNDECLARED"}
/ container_spec_memory_limit_bytes{container="___ UNDECLARED"}
```

**For GC-managed runtimes (JVM, .NET, Go):** `___ UNDECLARED` (insert heap profiler invocation)

**For native processes (C/C++/Rust/IoT):** `___ UNDECLARED` (insert valgrind / heaptrack / vendor tool invocation)

**Dashboard:** `___ UNDECLARED`

**Common causes:**
- Memory leak: objects accumulating without release (unbounded cache, event listener not removed, closure capturing references)
- Large object allocation not freed (image processing, ML inference batch)
- External data size growth (receiving larger payloads than expected)
- Fragmentation in long-running processes
- Third-party library leak
- IoT: dynamic allocation in interrupt context, stack overflow from deep recursion

---

## Remediation

### Leak pattern (memory grows continuously under constant load)
1. Capture heap snapshot via `___ UNDECLARED` before and after a request cycle.
2. Diff snapshots to identify retained objects.
3. Common fix locations: event listeners, caches without eviction policy, database result sets held in scope, closure capturing large objects.
4. Deploy fix; verify memory stabilizes over ___ UNDECLARED hours.

### High watermark pattern (spikes at peak, releases between)
1. This may be expected behavior — verify against declared memory budget.
2. If peak exceeds budget: optimize the high-allocation path identified in profiler.
3. Consider tuning GC thresholds or pre-allocating buffers.

### Immediate relief (critical — approaching OOM kill)
1. Rolling restart of affected instances: `___ UNDECLARED` (kubectl rollout restart / ECS force redeploy / equivalent).
2. Increase memory limit temporarily in `___ UNDECLARED` to prevent OOM kill while permanent fix is developed.
3. Scale out to distribute load across more instances.

### IoT
1. Review dynamic allocation in `___ UNDECLARED` — prefer static allocation for interrupt handlers.
2. Check for stack overflow: verify stack depth analysis in CI gate.
3. Enable watchdog if not already active.

---

## Escalation

- Memory > ___ % of limit and growing: page ___ UNDECLARED (imminent OOM kill)
- OOM kill has occurred: see `runbook-crash-rate-breach.md`; page ___ UNDECLARED

---

## Post-incident

- [ ] Leak source identified and patched
- [ ] Memory usage verified stable post-fix
- [ ] Performance budget updated if discovered that previous limit was too tight
- [ ] Memory profiling added to CI if not already present
- [ ] Runbook updated with leak pattern details for faster next diagnosis

---

*Generated from `_shared/templates/runbooks/runbook-memory-breach.md`. Replace all `___ UNDECLARED` with project-specific values before production use.*
