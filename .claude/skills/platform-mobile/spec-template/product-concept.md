# Product Concept Template (P0)

> **Platform:** Mobile | **Phase:** P0 — complete before design-document.md.
> Sections marked `[REQUIRED]` must be filled before Specify receipt.
> This document is the design authority. Mobile-specific: the platform choice (native vs. cross-platform) is a product decision made here, not an engineering decision made later.

---

## Product Statement [REQUIRED]

One sentence: what the app does, who uses it, and what outcome it produces.

> Example: "A medication reminder app for elderly users that reduces missed doses by escalating to a caregiver when no response is detected."

---

## Product Pillars [REQUIRED]

Declare 2–4 pillars. Each must be **falsifiable** — a real design decision must be able to fail it.

### Pillar 1: [Name]

**Definition:** One sentence stating what this pillar demands of every product decision.

**Falsifiability test:** "This design fails Pillar 1 if it [concrete failure condition]."

**Anti-pillar:** The app we explicitly refuse to build.

---

### Pillar 2: [Name]

**Definition:**

**Falsifiability test:**

**Anti-pillar:**

---

### Pillar 3: [Name] *(optional)*

**Definition:**

**Falsifiability test:**

**Anti-pillar:**

---

## Platform Decision [REQUIRED]

Declare the platform strategy here. This decision constraints the entire technical stack — it cannot be changed without significant rework.

**Target platforms:**
[ ] iOS only
[ ] Android only
[ ] iOS + Android (cross-platform)
[ ] iOS + Android (dual native codebases)

**Framework choice:**
[ ] React Native — Rationale: ___
[ ] Flutter — Rationale: ___
[ ] Swift/SwiftUI (iOS native) — Rationale: ___
[ ] Kotlin/Jetpack Compose (Android native) — Rationale: ___
[ ] Capacitor (web hybrid) — Rationale: ___

**Decision rationale:** Why this framework over alternatives? Reference: team capability, performance requirements, platform access needs (hardware APIs, background modes), time-to-market.

**Platform-first features** (things only possible on one platform — declare now to avoid late rewrites):
- iOS-only: ___
- Android-only: ___

---

## User Value Proposition [REQUIRED]

Complete: "Mobile users choose this app over [alternatives — including the web version if one exists] because [specific mobile advantage]."

The mobile advantage must be something the mobile context uniquely enables: location awareness, camera, offline use, push notifications, home screen presence, biometric auth, or native feel. If the app is just a web page in a container, declare that explicitly.

**Mobile advantage maps to:** Pillar ___

---

## Primary User [REQUIRED]

Role, context, session pattern, and what success looks like.

**Session pattern:** ___ sessions per day, ___ minutes per session (mobile sessions are typically shorter and more frequent than web)
**One-handed use?** Yes / No — affects navigation pattern, touch target placement
**Connectivity expectation:** Always-connected / Frequently offline / Intermittent (affects offline architecture from day 1)
**Age range:** ___ — affects text sizing defaults, touch target minimums, font choices

---

## Scope Tiers [REQUIRED]

| Tier | Description | Ships if... | Core value delivered? |
|---|---|---|---|
| **MVP** | Minimum that delivers the declared mobile advantage | Time or budget constraint | Yes |
| **v1** | App Store launch | Standard launch | Yes |
| **v2** | Post-launch expansion | Post-launch iteration | Yes — extended |

**MVP store submission requirements** (non-negotiable before MVP ships):
- Privacy policy URL
- App icon (all sizes)
- Screenshots (minimum set per store)
- Age rating questionnaire completed
- All declared permissions have usage description strings

---

## Connectivity Stance [REQUIRED]

Declare before design-document.md. This shapes architecture — offline-first cannot be bolted on.

**Connectivity model:**
[ ] Online-only — app is non-functional without connectivity (must show clear offline state)
[ ] Offline-capable — core features work offline, sync when connected
[ ] Offline-first — full functionality offline, sync is optional enhancement

**This decision affects:** State management choice, data persistence layer, sync conflict resolution strategy.

---

## GWT Acceptance Scenarios

```
Given: a first-time user installs and opens the app
When: they spend 5 minutes using it
Then: they complete the primary use case without consulting documentation
      AND they grant only the permissions explicitly required for that use case

Given: the platform choice (framework) is made
When: it is evaluated against declared pillar requirements
Then: the chosen framework enables all Pillar 1 features on all declared platforms
      AND no pillar feature requires a capability the framework cannot provide

Given: development stops at MVP tier
When: the app is submitted to both stores
Then: all store submission requirements are met
      AND the declared mobile advantage is present and functional
      AND the connectivity stance is honored without crashes when offline (if online-only: clear error message)
```

---

## Open Questions

Platform decisions and pillar definitions that are unresolved. Specify receipt blocked until REQUIRED sections complete.
