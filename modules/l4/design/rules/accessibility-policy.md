# Gateway Design — Accessibility Policy

Rules enforced by gateway-design Phase B verdict. WCAG 2.1 AA is the minimum floor for all visual targets. Violations produce FLAG or BLOCK verdicts.

---

## Rule X1: Keyboard Navigation Audit

**Requirement:** All interactive elements and user flows must be fully operable by keyboard.

| Requirement | Details |
|---|---|
| Tab order | Logical tab order follows visual reading order; no tab traps |
| Focus indicator | Visible focus indicator present on all interactive elements; browser default not overridden without replacement |
| Skip navigation | "Skip to main content" link present on every page/view with repeated navigation |
| Keyboard shortcuts | Any custom keyboard shortcuts must not conflict with browser or OS shortcuts; must be discoverable |

**Verifier check:** Navigate entire primary user flow using Tab, Shift+Tab, Enter, Space, and arrow keys only. All tasks must be completable.

**Failure modes:**
- Tab trap (focus enters a component and cannot exit with keyboard) = BLOCK
- Focus indicator removed with `outline: none` and no replacement = BLOCK
- Skip navigation absent on pages with repeated navigation = FLAG
- Interactive element not reachable via Tab = BLOCK

---

## Rule X2: Touch Target Minimums

**Requirement:** All interactive elements on touch surfaces must meet minimum target size requirements.

| Surface | Minimum target size | Notes |
|---|---|---|
| Mobile (iOS / Android) | 44x44 CSS pixels | WCAG 2.1 AA (SC 2.5.5) and Apple HIG requirement |
| Desktop with touch screen | 44x44 CSS pixels | Same floor |
| Desktop (pointer-only) | 24x24 CSS pixels | WCAG 2.1 AA minimum for pointer targets |

**Exception:** Inline text links within paragraphs are exempt from touch target minimums; padding must be added where feasible without disrupting layout.

**Failure modes:**
- Touch target below 44x44px on mobile targets = BLOCK
- Icon-only buttons below 44x44px on any touch surface = BLOCK
- Interactive elements with `font-size: < 12px` making them impossible to hit = FLAG

---

## Rule X3: Focus Management on State Changes

**Requirement:** When UI state changes programmatically (modal opens, panel expands, page section updates), focus must be managed explicitly.

| State change | Required focus behavior |
|---|---|
| Modal / dialog opens | Focus moves to modal; trapped inside until closed |
| Modal / dialog closes | Focus returns to the trigger element |
| Route change (SPA) | Focus moves to main heading or page landmark |
| Alert / notification | Focus moves to alert if it requires action; passive notifications do not steal focus |
| Dynamic content added to DOM | `aria-live` region used for non-disruptive announcements; focus moved only when user action caused the change |

**Failure modes:**
- Modal focus not trapped inside the modal = BLOCK
- Focus not returned to trigger element on modal close = FLAG
- SPA route change with no focus management = FLAG
- `aria-live` region absent for dynamic content that conveys status = FLAG

---

## Rule X4: Gesture Alternatives

**Requirement:** No functionality may be available through gestures only. All gesture-based interactions must have a non-gesture alternative.

| Gesture | Required alternative |
|---|---|
| Swipe to dismiss | Close button or keyboard shortcut |
| Long press | Context menu accessible via secondary button or keyboard |
| Pinch to zoom | Zoom controls in UI; browser native zoom must not be blocked |
| Pull-to-refresh | Refresh button |
| Custom multi-finger gesture | Equivalent action accessible via single tap/click |

**Failure modes:**
- `user-scalable=no` or `maximum-scale=1` in viewport meta tag = BLOCK (blocks browser zoom; WCAG SC 1.4.4 violation)
- Swipe-to-dismiss as only dismissal mechanism = BLOCK
- Any primary action accessible only via gesture without alternative = BLOCK

---

## Rule X5: ARIA Role and Label Completeness

**Requirement:** All interactive and landmark elements must have correct ARIA roles, labels, and states.

| Element type | Requirement |
|---|---|
| Buttons with icon only | `aria-label` required |
| Images that convey information | `alt` text required; empty `alt=""` only for decorative images |
| Form inputs | `<label>` associated via `for`/`id` or `aria-label`; `aria-required` when required |
| Dialog / modal | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` pointing to dialog title |
| Live regions | `aria-live="polite"` for status messages; `aria-live="assertive"` only for critical alerts |
| Expandable components | `aria-expanded` state reflects current open/closed state |

**Failure modes:**
- Icon-only button without `aria-label` = BLOCK
- Informational image without `alt` = BLOCK
- Form input without associated label = BLOCK
- `aria-live="assertive"` on non-critical content = FLAG (causes screen reader interruption)
