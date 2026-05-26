# Acceptance Tests — Gateway: Aesthetic (L4)

## AT-AES-GW-01: Does not activate on non-visual targets

**Given** a build target of type API-Service, CLI, IoT, Library, or Data-Pipeline
**When** Recipe processes the target
**Then** the Aesthetic gateway does not activate unless a visual component is explicitly declared in scope

---

## AT-AES-GW-02: Always activates on visual targets

**Given** a build target of type Web, Mobile, Desktop, Game, or Extension/Plugin
**When** Recipe processes the target
**Then** the Aesthetic gateway activates unconditionally

---

## AT-AES-GW-03: L3 platform receipt required before activation

**Given** an Aesthetic gateway invocation
**When** no L3 platform receipt exists
**Then** the gateway FAILs Phase A — it activates on top of, not instead of, the platform package

---

## AT-AES-GW-04: Raw visual values in component code are BLOCK

**Given** Aesthetic gateway Phase B evaluating component code
**When** raw color hex, pixel values, or font-size values appear directly in component code rather than as token references (rule T1 from design-token-policy.md)
**Then** verdict is BLOCK — all visual values must be expressed as design tokens

---

## AT-AES-GW-05: WCAG AA contrast check enforced

**Given** Aesthetic gateway Phase B
**When** a color combination fails the 4.5:1 contrast ratio for normal text (rule V3 from visual-standards-policy.md)
**Then** the finding produces BLOCK verdict — accessibility contrast is a hard gate, not advisory

---

## AT-AES-GW-06: Dark mode scope must be declared

**Given** Aesthetic gateway Phase B evaluating a project with color tokens
**When** dark mode scope is not declared (rule V4)
**Then** the finding produces FLAG verdict

---

## AT-AES-GW-07: Aesthetic does not own UX/interaction concerns

**Given** an Aesthetic gateway run on a Web project
**When** the gateway evaluates the project
**Then** it does not audit touch targets, keyboard navigation, or user flow depth — those are owned by the Design gateway

---

## AT-AES-GW-08: Homowabian ultra mode suppressed

**Given** an Aesthetic gateway producing prose output about visual design decisions
**When** Homowabian register is active
**Then** ultra mode is suppressed — full prose context is required for visual design decisions

---

## AT-AES-GW-09: Gateway receipt contains all gate results

**Given** a completed Aesthetic gateway Phase B
**Then** the `gateway-verdict-receipt` contains:
- `gateway`
- `phase`
- `verdict` (PASS | FLAG | BLOCK)
- `brand_asset_check`
- `color_token_check`
- `contrast_check`
- `dark_mode_scope_declared`
- `motion_tokens_check`
- `platform_receipt_verified`
