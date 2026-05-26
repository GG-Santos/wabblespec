# Acceptance Tests — Gateway: Design (L4)

## AT-DES-GW-01: Activates unconditionally on visual targets

**Given** a build target of type Web, Mobile, Desktop, Game, or Extension/Plugin
**When** Recipe processes the target
**Then** the Design gateway activates — no explicit command required

---

## AT-DES-GW-02: L3 platform receipt required before activation

**Given** a Design gateway invocation
**When** no L3 platform receipt exists
**Then** the gateway FAILs Phase A — it activates on top of, not instead of, the platform package

---

## AT-DES-GW-03: Design gateway owns interaction; Aesthetic gateway owns visuals

**Given** a project with both Design and Aesthetic gateways active
**When** the Design gateway evaluates the project
**Then** it audits mental models, information architecture, interaction patterns, keyboard navigation, and accessibility baseline; it does not audit brand assets, color tokens, or typography — those belong to Aesthetic

---

## AT-DES-GW-04: Navigation depth limit enforced

**Given** Design gateway Phase B evaluating an information architecture
**When** any P0 user flow requires more than 3 navigation levels to complete (rule U3 from ux-standards-policy.md)
**Then** verdict is FLAG — IA depth limit applies to primary flows

---

## AT-DES-GW-05: No tab traps is a BLOCK condition

**Given** Design gateway Phase B evaluating keyboard navigation
**When** a tab trap is present (keyboard focus becomes unreachable/unescapable, rule X1 from accessibility-policy.md)
**Then** verdict is BLOCK — keyboard trap is an accessibility hard gate

---

## AT-DES-GW-06: user-scalable=no is a BLOCK condition

**Given** Design gateway Phase B evaluating mobile viewport settings
**When** `user-scalable=no` or `maximum-scale=1` is present in the viewport meta tag (rule X4)
**Then** verdict is BLOCK — disabling user zoom is a WCAG failure

---

## AT-DES-GW-07: Storybook required for 10+ components

**Given** Design gateway Phase B evaluating a component library
**When** the project has 10 or more UI components and no Storybook (rule U5)
**Then** verdict is FLAG — design system governance requires Storybook at this scale

---

## AT-DES-GW-08: Phase A loads three reference files

**Given** Design gateway Phase A
**When** knowledge injection runs
**Then** flows.md, components.md, and systems.md are all loaded into Specify context before the gateway-spec-receipt is written

---

## AT-DES-GW-09: Gateway receipt contains all gate results

**Given** a completed Design gateway Phase B
**Then** the `gateway-verdict-receipt` contains:
- `gateway`
- `phase`
- `verdict` (PASS | FLAG | BLOCK)
- `mental_model_gaps_declared`
- `ia_depth_check`
- `keyboard_navigation_check`
- `touch_targets_check`
- `accessibility_floor_pass`
- `platform_receipt_verified`
