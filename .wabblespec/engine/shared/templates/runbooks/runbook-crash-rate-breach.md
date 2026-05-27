# Runbook: Crash Rate Breach

**Alert:** `CrashRateBreach`  
**Severity:** critical  
**SLO:** Crash-free rate ≥ ___ % — declared in `engineering/performance-budgets.md`  
**Owner:** ___ UNDECLARED  
**Last reviewed:** ___ UNDECLARED  
**Applies to:** Mobile, Desktop, IoT, Game platforms primarily; also applies to server processes with crash monitoring

---

## Symptoms

- Crash reporting dashboard showing crash-free rate below declared threshold
- `crash_free_rate` metric dropping below SLO (e.g., 99.5% for mobile)
- Crash reporting tool (`___ UNDECLARED`: Firebase Crashlytics / Sentry / Bugsnag / custom) showing new crash signature
- User reports of app force-closing or unresponsive behavior
- For server processes: container/pod restart count elevated, OOM kill events in infrastructure logs

---

## Immediate triage

1. Confirm crash signature is new — not a known, pre-existing issue already tracked.
2. Check deployment log — was a release or OTA update within the last 24h?
3. Identify affected scope: all users, specific device type/OS version, specific app version?
4. Check crash volume: how many unique users affected?
5. Is there a single dominant crash signature or multiple?

---

## Diagnosis

**Crash reporting query:** `___ UNDECLARED` (insert crash aggregation query in your crash tool)

**Identify top crash signature:**
- Stack trace: `___ UNDECLARED`
- Affected app version: `___ UNDECLARED`
- Affected OS/platform version: `___ UNDECLARED`
- First seen: `___ UNDECLARED`
- Impacted user %: `___ UNDECLARED`

**For server OOM crashes:**
```
# Pod OOM kills (Kubernetes)
kubectl get events --field-selector reason=OOMKilling -n ___ UNDECLARED
```

**Dashboard:** `___ UNDECLARED`

**Common causes (client apps):**
- Null pointer / force unwrap on data that can be absent
- Unhandled exception in a new code path introduced in the release
- Memory leak reaching device limit (especially low-RAM devices)
- Third-party SDK crash in updated dependency
- Race condition under specific concurrency timing
- OS API behavior change in new OS version

**Common causes (server processes):**
- Memory leak reaching container limit (OOM kill)
- Unhandled exception in async handler / goroutine / thread
- Native dependency crash (native extension, JNI, FFI)
- Watchdog timeout (IoT: process not checking in)

---

## Remediation

### Client app (mobile/desktop/game)
1. If a single dominant crash signature from recent release: initiate rollback or hotfix.
   - OTA rollback: `___ UNDECLARED` (if OTA signing and rollback configured)
   - Force app update: push hotfix build through `___ UNDECLARED` distribution pipeline
2. If crash is on a specific OS version only: add version guard in `___ UNDECLARED` and disable the affected feature for that version.
3. If third-party SDK crash: pin to previous SDK version in `___ UNDECLARED`, redeploy.
4. If memory leak: add memory profiling build and identify allocation source via `___ UNDECLARED`.

### Server process
1. If OOM: increase memory limit in `___ UNDECLARED`, redeploy; also profile for leak via `___ UNDECLARED`.
2. If unhandled exception: add crash handler / recover mechanism in `___ UNDECLARED`; fix root cause.
3. If watchdog timeout (IoT): check watchdog feed frequency in `___ UNDECLARED`; verify process is not blocking.

---

## Escalation

- Crash-free rate < ___ % (below hard floor): page ___ UNDECLARED immediately
- Crash affecting > ___ % unique users: open severity-1 incident
- Crash in payment / auth / safety-critical feature: page ___ UNDECLARED immediately

---

## Post-incident

- [ ] Crash signature resolved and verified in next release
- [ ] Crash-free rate recovered above SLO threshold
- [ ] Root cause documented (null handling / memory / dependency / race condition)
- [ ] Regression test added for the exact crash path
- [ ] Crash reporting alert thresholds reviewed
- [ ] Runbook updated with new learnings

---

*Generated from `.wabblespec/engine/shared/templates/runbooks/runbook-crash-rate-breach.md`. Replace all `___ UNDECLARED` with project-specific values before production use.*
