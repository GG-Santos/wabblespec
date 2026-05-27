# Game Security — Threat Model

## Threat Surface

Games face unique security concerns centered on fairness (cheating), economy (fraud), and player safety (harassment, account theft).

1. **Speed/position hacks** — client manipulates game state to move faster or teleport
2. **Aimbot/wallhack** — client reads memory to gain unfair information advantage
3. **Economy fraud** — exploiting bugs in economy/crafting to duplicate items or currency
4. **Account theft** — stolen credentials, session hijacking
5. **DDoS against game servers** — flooding server to cause disconnections
6. **Save file manipulation** — editing local save files for singleplayer advantage (scope: player's own game only — not a security concern for singleplayer)
7. **Client memory tampering** — modifying game memory values (health, ammo, currency)

---

## Threat 1: Speed/Position Hacks

**Description:** Player modifies client-side movement variables or sends fabricated position updates to server.

**Mitigations (multiplayer):**
- Server validates all position updates: distance from last position ÷ time elapsed ≤ max_speed + tolerance
- Server never trusts client position — server simulates or validates every frame
- Reject inputs implying impossible movement; apply server-authoritative correction

**Singleplayer:** Not a security concern — player is cheating against themselves.

---

## Threat 2: Economy Fraud

**Description:** Player exploits race conditions, integer overflow, or transaction bugs to duplicate items or currency.

**Mitigations:**
- All economy transactions server-side only. Client requests transactions; server executes.
- Transactions atomic (ACID). No partial-success states.
- Server validates: player has sufficient balance before deducting.
- Rate limiting: max N transactions per second per player.
- Audit log: every economy transaction logged with before/after state.

---

## Threat 3: Account Theft

**Description:** Player accounts stolen via credential stuffing, phishing, or weak session management.

**Mitigations:**
- Auth via platform accounts (Steam/PSN/Xbox Live) wherever possible — offloads auth security
- JWT or platform tokens for session auth — not username/password sessions
- Rate limit login attempts. Lock after N failures.
- Anomalous login detection (new device, new country).

---

## Threat 4: Client Memory Tampering

**Description:** Player uses Cheat Engine or similar to modify in-memory values (health = 9999, ammo = unlimited).

**Mitigations (singleplayer):** Policy decision — many games allow this. Declare scope.

**Mitigations (multiplayer):** Server is authoritative — client memory values do not affect server state. Client memory tampering only affects client's own display, not actual game state.

**Anti-cheat software (optional):** Kernel-level anti-cheat (EAC, BattlEye) detects memory editors. Invasive — requires clear disclosure to players. Suitability depends on genre and player expectations.

---

## Threat 5: DDoS Against Game Servers

**Description:** Attackers flood game server with traffic, causing disconnections for all players.

**Mitigations:**
- DDoS protection at network edge (Cloudflare, AWS Shield)
- Player IPs never exposed — route all traffic through relay servers
- Rate limiting per connection
- Server capacity auto-scaling to absorb traffic spikes
