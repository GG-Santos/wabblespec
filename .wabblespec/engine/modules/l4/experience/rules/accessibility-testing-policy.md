# Gateway Experience — Accessibility Testing Policy

Rules enforced by gateway-experience Phase B verdict. Supplements the Design gateway's WCAG 2.1 AA floor with deep accessibility validation: screen reader matrix, color blindness simulation, cognitive, and motor accessibility. Applies to visual targets with user research declared in scope.

---

## Rule AT1: Screen Reader Testing Matrix

**Requirement:** Every visual target must be tested with the screen reader and browser combinations relevant to its declared platforms.

**Minimum test matrix:**

| Platform | Screen reader | Browser | Priority |
|---|---|---|---|
| Windows | NVDA | Firefox | Required |
| Windows | JAWS | Chrome | Required for enterprise targets |
| macOS / iOS | VoiceOver | Safari | Required |
| Android | TalkBack | Chrome | Required for mobile targets |
| Linux | Orca | Firefox | Optional |

**What to test per screen reader:**
- Primary user flow: all steps completable using screen reader navigation only
- Forms: all labels announced; errors announced at field level
- Dynamic content: live region announcements present and not excessive
- Navigation: heading structure logical; landmark regions present

**Failure modes:**
- Primary user flow not completable with NVDA + Firefox = BLOCK
- Screen reader test results not documented per session = FLAG
- Screen reader testing performed only with automated tools (axe, Lighthouse) and no manual session = FLAG (automated tools detect ~40% of accessibility issues)

---

## Rule AT2: Color Blindness Simulation Testing

**Requirement:** All primary user flows and information-bearing visualizations must be tested with color blindness simulation for the three most prevalent types.

| Type | Prevalence | Simulation tool |
|---|---|---|
| Deuteranopia (green-weak) | ~5% male | Figma plugin, Coblis, browser DevTools |
| Protanopia (red-weak) | ~1% male | Same tools |
| Achromatopsia (complete) | Rare | Same tools |

**Requirements:**
- Information must not be conveyed by color alone; shape, pattern, or text label must also differentiate
- Charts and data visualizations: legend labels present; no red-green color pairs as the only differentiation
- Status indicators (success/error): icon or text label accompanies color

**Failure modes:**
- Information conveyed by color alone (no non-color alternative) = BLOCK
- Data visualization relying solely on red/green differentiation = BLOCK
- Color blindness simulation not performed for any visual component conveying data = FLAG

---

## Rule AT3: Cognitive Accessibility

**Requirement:** All user-facing content and flows must meet cognitive accessibility requirements.

| Requirement | Details |
|---|---|
| Reading level | Body copy at or below Grade 8 reading level (Flesch-Kincaid or equivalent) for general-audience products; technical products may be higher with justification |
| Instructions | Step-by-step instructions written as numbered lists; no reliance on memory between steps |
| Error messages | Explain what went wrong and how to fix it; no error codes as the only explanation |
| Timeouts | Any session timeout must warn the user at least 20 seconds before expiry; provide option to extend |
| Consistent navigation | Navigation labels and positions consistent across all screens |
| Cognitive load | Critical flows limited to one primary decision per step; no step presents more than 5–7 options without grouping |

**Failure modes:**
- Session timeout with no warning = BLOCK
- Error message with code only (e.g., "Error 403") and no explanation = BLOCK
- Navigation labels that change meaning between pages = FLAG
- Multi-step flow with more than 7 options on a single decision step with no grouping = FLAG

---

## Rule AT4: Motor Accessibility

**Requirement:** All interactive elements must be operable by users with limited motor control.

| Requirement | Details |
|---|---|
| No time-limited interactions | No interaction that requires precise timing (e.g., double-click within 200ms); if present, provide alternative |
| Drag-and-drop alternatives | Any drag-and-drop interaction must have a keyboard or button alternative |
| Click/tap target spacing | Minimum 8px gap between adjacent interactive elements (prevents mis-activation) |
| Pointer precision | No interaction requiring precise pointer positioning (e.g., a resize handle with < 4px hit area) |
| Switch access | Complex interactions (drag, resize, multi-select) must be operable with switch access (single-switch scanning or two-switch row/column) for any target declaring accessibility support level AAA |

**Failure modes:**
- Drag-and-drop with no alternative = BLOCK
- Adjacent interactive elements with no spacing gap = FLAG
- Time-limited interaction with no alternative = BLOCK
- Resize handles with hit area < 4px = FLAG
