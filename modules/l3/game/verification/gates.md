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

## Gate Summary

| Gate | Description | Blocking |
|---|---|---|
| 1 | Frame rate target met | Yes |
| 2 | Memory within budget | Yes |
| 3 | Save/load integrity | Yes |
| 4 | Load time within budget | Yes |
| 5 | Server input validation | Yes (multiplayer) |
| 6 | Anti-cheat scope matches declaration | Yes |
| 7 | Platform certification checklist | Yes (console) |
| 8 | Build size within budget | Yes |
| 9 | 1-hour soak test — no crash | Yes |

All gates are blocking. No Delivery wave proceeds with any gate in FAIL state.
