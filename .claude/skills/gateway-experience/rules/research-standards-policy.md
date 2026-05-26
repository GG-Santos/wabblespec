# Gateway Experience — Research Standards Policy

Rules enforced by gateway-experience Phase B verdict. Applies to visual-facing targets where user research is declared in scope at P1. Violations produce FLAG or BLOCK verdicts.

---

## Rule R1: Research Method Selection

**Requirement:** Every research engagement must declare which method is being used, why it was selected for the stated research question, and the expected output.

**Approved research methods and appropriate research questions:**

| Method | Appropriate for |
|---|---|
| Moderated usability test | Task completion, think-aloud insight, pain point identification |
| Unmoderated usability test | Larger sample task completion; behavioral data at scale |
| Contextual inquiry | Understanding existing workflows in the user's real environment |
| Diary study | Longitudinal behavior, infrequent tasks, emotional journey |
| Survey (quantitative) | Measuring prevalence of attitudes or behaviors across large population |
| Card sorting | Information architecture validation |
| Tree testing | Navigation structure validation without visual design influence |
| First-click testing | Landing page or home screen effectiveness |

**Failure modes:**
- Research method not declared for a declared research objective = FLAG
- Qualitative method used to claim quantitative significance (e.g., "5 users confirmed X is the primary problem") = FLAG
- Research method selected without stated fit to the research question = FLAG

---

## Rule R2: Usability Test Scenario Requirements

**Requirement:** Every usability test session must have written scenarios and success metrics before the session begins.

| Requirement | Details |
|---|---|
| Scenarios | Written as realistic task descriptions (not "click on the button"); no leading language |
| Success metrics | At minimum: task completion rate (binary: completed / did not complete) |
| Secondary metrics | Time on task, error count, satisfaction rating (declared before sessions, not after) |
| Sample size | Minimum 5 participants for qualitative usability studies; minimum 30 for quantitative task metrics |
| Participant criteria | Screener criteria match the declared target user persona |

**Failure modes:**
- Usability test conducted without written scenarios = BLOCK
- Success metric declared after sessions (post-hoc) = BLOCK
- Sample size below 5 for qualitative test without written justification = FLAG
- Participants recruited without screener matching target persona = FLAG

---

## Rule R3: Satisfaction Measurement Coverage

**Requirement:** Any production release affecting a core user flow must include a satisfaction measurement mechanism.

**Permitted measurement instruments:**

| Instrument | Use case |
|---|---|
| System Usability Scale (SUS) | Holistic product usability benchmark (10-question standardized scale) |
| Net Promoter Score (NPS) | Relationship loyalty measurement |
| Customer Effort Score (CES) | Task-specific effort perception |
| In-product microsurvey | Post-task or post-interaction satisfaction (1–5 rating + optional open-text) |
| Session replay + behavioral metrics | Behavioral proxy for satisfaction (rage clicks, drop-off points) |

**Failure modes:**
- Core user flow modified with no satisfaction measurement plan = FLAG
- Satisfaction instrument added post-launch as the only measurement (no baseline) = FLAG
- SUS score below 68 (industry average) with no improvement plan in spec = FLAG

---

## Rule R4: Research Insights Written to Memory

**Requirement:** All completed research produces insights written to Memory as FRESH drawers, not left as informal notes.

| Requirement | Details |
|---|---|
| Drawer per study | Each completed research study produces one or more Memory drawers |
| Freshness status | All research drawers start as FRESH; expire per standard memory policy |
| Insight format | Each drawer: research question, method used, participants, key insights (not raw data), recommended actions |
| Linkage | Insights linked to the features or flows they informed via drawer tags |

**Failure modes:**
- Research completed but insights not written to Memory = FLAG
- Research drawer without a linked recommended action = FLAG
- Insights stored as Markdown files in the repo rather than Memory drawers = FLAG (prevents Dream consolidation)
