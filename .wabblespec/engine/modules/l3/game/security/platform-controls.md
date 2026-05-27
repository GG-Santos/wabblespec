# Game Security — Platform Controls

---

## Control 1: Server Authority for All Competitive State

**Rule:** In multiplayer games, server is the sole authority for all state that affects fairness: position, health, ammo, score, economy.

**Client role:** Send inputs only. Display server-provided state. Predict locally for responsiveness but reconcile with server.

**Prohibited:** Client-authoritative health, client-authoritative position in competitive play.

---

## Control 2: Input Validation on Server

**Rule:** Server validates all player inputs before applying to game state.

**Validation checklist per input type:**
- Movement: distance/time ≤ max_speed + tolerance
- Action (shoot, attack): player has the required resource (ammo, cooldown elapsed)
- Economy action: player has sufficient balance, item exists in their inventory
- Timestamp: input timestamp within ± acceptable window of server time

---

## Control 3: Economy Transaction Atomicity

**Rule:** All economy transactions (buy, sell, trade, craft) are atomic server-side. No partial success.

```sql
BEGIN TRANSACTION;
  UPDATE inventory SET quantity = quantity - 1 WHERE player_id = ? AND item_id = ? AND quantity >= 1;
  IF ROW_COUNT = 0 THEN ROLLBACK;
  UPDATE player SET currency = currency + sell_price WHERE player_id = ?;
COMMIT;
```

---

## Control 4: Anti-Cheat Scope Declaration

**Rule:** Anti-cheat scope explicitly declared in design-document.md.

Options:
- `server-authoritative`: server validates inputs — no client-side anti-cheat needed for fairness
- `kernel-level`: EAC/BattlEye — document player disclosure requirement
- `none-singleplayer-only`: explicitly documented, no competitive integrity concern

**No anti-cheat** is acceptable for singleplayer games. "Theater" anti-cheat (client-side only, easily bypassed) must be labeled as such.

---

## Control 5: Player IP Protection

**Rule:** Player IP addresses must not be exposed to other players.

**Implementation:** All peer connections routed through relay server. No direct P2P connections that reveal IP.

---

## Control 6: Save File Integrity

**Rule:** Save files include checksum. Game detects corruption and falls back to backup.

**Implementation:** CRC32 checksum in save file header. Atomic write (temp → validate → rename).

**Singleplayer save editing:** Policy decision. If save editing is intended to be possible, document it. If not, checksum provides detection (not prevention — determined players can recalculate).

---

## Control 7: Age-Appropriate Content

**Rule:** Age rating obtained for all target platforms before release. Content complies with declared rating.

**Enforcement:** Age rating body submission (ESRB, PEGI, CERO) is part of release gate. Console certification requires valid age rating.
