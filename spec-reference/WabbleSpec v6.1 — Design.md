# WabbleSpec v6.1 — Design

**Gateway:** Design
**Layer:** L4 Capability
**Tier:** 1 — CRITICAL ROUTING
**Document scope:** Design gateway — UX, interaction design, information architecture, user flows, design system

---

## Overview

The Design gateway owns UX and interaction standards: user mental models, information architecture, interaction patterns, accessibility baseline, and design system governance. It applies to all visual-facing targets — Web, Mobile, Desktop, Game, Extension/Plugin. The Design gateway is distinct from the Aesthetic gateway: Aesthetic owns the visual language, Design owns how things work and how users move through them.

**In scope:**
- UX principles (mental models, affordances, feedback, error states)
- Information architecture (navigation depth, labeling, search thresholds)
- Interaction design (touch targets, keyboard access, focus management, gestures)
- Design system governance (component library, documentation, token consumption)
- Accessibility baseline (WCAG 2.1 AA, keyboard navigation, screen reader, no accessibility-only paths)

**Applies to:** Web, Mobile, Desktop, Game, Extension/Plugin build targets.

---

## Gateway Structure

```
.wabblespec/gateways/design/
  SKILL.md
  skill-rules.json
  references/
    ux-principles.md
    information-architecture.md
    interaction-design.md
    design-system.md
  rules/
    accessibility-floor.md
  evaluations/
  schemas/
    receipt.schema.json
```

---

## Activation

`skill-rules.json` triggers Design gateway on:
- Visual-facing build target (Web, Mobile, Desktop, Game, Extension/Plugin)
- P1 Design Document stage — user flows required
- P3 Technical Spec — interaction patterns applied
- Explicit `/design` command

---

## UX Principles

**Reference:** `references/ux-principles.md`

### User Mental Models

Target mental model declared per major flow in spec at P1. A mental model is the user's existing understanding of how the domain works — the design should match it or explicitly bridge the gap.

Declaration format:

```markdown
## User Mental Model — <flow name>

**Assumed model:** <what the user expects based on prior experience>
**Actual model:** <how the system actually works>
**Gap:** <where they diverge>
**Bridge strategy:** <how the UI helps the user cross the gap>
```

No undeclared mental model gaps. If the system behaves differently from user expectations, the gap is declared and the bridge strategy is documented.

### Affordances

Interactive elements visually communicate their affordance:
- Buttons look clickable (visual weight, color, cursor)
- Links look followable (underline, color, cursor)
- Inputs look fillable (border, background, placeholder)
- Drag handles look draggable (grip icon, cursor)

No interactive element that looks non-interactive. No non-interactive element that looks interactive.

### Feedback

Every user action has feedback within 100ms perceived (immediate response). For actions that take longer:
- 0–100ms: no indicator needed
- 100ms–1s: spinner or progress indication
- > 1s: progress indicator with cancellation option if possible
- > 10s: time estimate if knowable

No silent actions. No action that completes without any visible state change.

### Error States

Every error has a message. Every message has a recovery path. Required per error type:

| Error type | Required elements |
|---|---|
| Validation error | Inline, near the field, explains what is wrong and how to fix |
| Network error | User-facing message, retry option, what data was lost (if any) |
| Not found | Explanation, navigation path back to safety |
| Permission error | Explanation, path to request access or contact admin |
| System error | Apology, reference ID for support, what the user can do now |

Generic "Something went wrong" without a recovery path is not an acceptable error state.

---

## Information Architecture

**Reference:** `references/information-architecture.md`

### Navigation Depth

Maximum 3 levels deep for primary navigation. Users should be able to reach any primary destination in 3 clicks or fewer from the home state. If more than 3 levels are needed, the IA needs restructuring — not a deeper nav.

### Labeling

Content labels derived from:
- User research vocabulary (what users call things)
- Domain vocabulary (accepted industry terms)
- Not internal jargon (team names, code names, backend model names)

Audit: every label reviewed against user vocabulary at P1. Technical labels that appear in the UI are flagged for user vocabulary review.

### Search and Filter

Required when content exceeds 20 items in a list or grid. Search or filter — both not required, but at least one required. Threshold declared in spec:

```markdown
**Search required at:** 20 items
**Filter required at:** 20 items
**Both required at:** 50+ items or multi-dimensional content
```

---

## Interaction Design

**Reference:** `references/interaction-design.md`

### Touch Targets

| Platform | Minimum size |
|---|---|
| Mobile | 44×44px (Apple HIG and Android Material) |
| Desktop with touch | 44×44px |
| Desktop mouse-only | 32×32px, with keyboard alternative |

Touch target is the interactive area, not the visual size. A small icon can have a larger invisible hit area.

### Keyboard Access

All interactions keyboard-accessible. No mouse-only or touch-only interactions. Keyboard audit required before delivery:
- Tab order is logical (follows visual/reading order)
- All interactive elements reachable by Tab/Shift-Tab
- Enter and Space activate buttons and links as expected
- Arrow keys navigate within menus, listboxes, and grids
- Escape closes modals, dropdowns, and overlays

### Focus Management

Focus lands on a meaningful element after every state change:
- Modal opens: focus moves to modal heading or first interactive element
- Modal closes: focus returns to the trigger element
- Page navigation: focus moves to main content or page heading
- Error appears: focus moves to error message or first invalid field

No focus that moves to a decorative or non-interactive element.

### Gesture Design

No gesture-only interactions. Every gesture has a visible button or control equivalent:

| Gesture | Required equivalent |
|---|---|
| Swipe to delete | Delete button in row or context menu |
| Swipe to reveal actions | Actions available via context menu or edit mode |
| Pull to refresh | Refresh button |
| Pinch to zoom | Zoom controls |
| Long press | Right-click or context menu equivalent |

Custom gestures must be discoverable — not assumed.

---

## Design System

**Reference:** `references/design-system.md`

### Component Library Declaration

Declared at P1 — one of:

| Option | Definition |
|---|---|
| Existing library | Named library adopted (Radix, shadcn/ui, MUI, etc.) — version pinned |
| Build from scratch | Custom component library — scope and timeline declared |
| Headless + styled | Headless library for behavior + custom styles — declared |

Not declared = build from scratch. Explicit decision required — default has cost implications.

### Component Documentation

Each component in the design system has:
- Usage guidelines (when to use, when not to use)
- Props/API documentation
- Do/don't examples (at least one each)
- Accessibility notes (keyboard behavior, ARIA, screen reader behavior)

### Storybook or Equivalent

Required for projects with >= 10 custom components. Storybook (or equivalent — Histoire, Ladle, Chromatic) declared in spec when threshold is met. Stories cover:
- Default state
- All significant variants
- Error states
- Loading states
- Edge cases (empty, long content, RTL if in scope)

### Token Consumption

Components consume Aesthetic gateway tokens — not raw values. Design system components are not exempt from the design token policy. Components consume semantic tokens from the Aesthetic gateway.

---

## Accessibility Floor

**Reference:** `rules/accessibility-floor.md`

WCAG 2.1 AA is the minimum baseline for all visual targets. Non-negotiable. Cannot be waived by project decision.

| Requirement | What it means |
|---|---|
| Keyboard navigation | Every interactive element reachable and operable by keyboard |
| Screen reader | Semantic HTML or ARIA where HTML semantics insufficient |
| Color contrast | Aesthetic gateway contrast requirements (4.5:1 text, 3:1 UI) |
| Reduced motion | Aesthetic gateway reduced motion requirements |
| Focus indicators | Visible focus ring on all interactive elements (browser default or custom) |
| Form labels | Every input has an associated label (not placeholder-only) |
| Images | Alt text for informational images, `alt=""` for decorative |
| Tables | `scope` attributes, captions where appropriate |

**No accessibility-only paths:** Accessibility is integrated into the primary experience, not a separate mode or toggle. An "accessible version" of a page is not an acceptable approach.

---

## Integration Points

| Module | Relationship |
|---|---|
| Apply | Apply reads Design gateway for routing during UX execution |
| Verifier | Verifier Demonstration mode includes user flow completability and keyboard nav checks |
| Aesthetic gateway | Design system components consume Aesthetic tokens; gateways are coordinated, not merged |
| Experience gateway | Experience gateway runs usability testing against flows declared in Design |
| Platform packages (L3) | Platform determines interaction patterns (Mobile uses native navigation patterns; Desktop may use platform-specific controls) |
| Specify | Specify reads Design gateway when classifying interaction changes as BREAKING |

---

## Verification Mode

**Demonstration** — user flows completable end-to-end, keyboard navigation audit passes, touch targets meet minimums, design system documented, accessibility floor met.

---

## Receipt Extension Fields

```json
{
  "user_flows_documented": 0,
  "wcag_level": "AA",
  "keyboard_audit_passed": true,
  "design_system_declared": true
}
```

---

## Cross-References

- Aesthetic gateway (visual language, design tokens): `WabbleSpec v6.1 — Aesthetic.md`
- Experience gateway (usability testing, research): `WabbleSpec v6.1 — Experience.md`
- L3 Platform packages (platform-specific interaction patterns): `WabbleSpec v6.1 — Platform.md`
- Verification modes (Demonstration): `WabbleSpec v6.1 — Core.md` § Verification Modes
