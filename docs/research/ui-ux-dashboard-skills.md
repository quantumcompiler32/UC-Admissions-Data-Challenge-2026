# UI/UX Skills and Workflow for a Polished UC Admissions Dashboard

**Research date:** 2026-08-30
**Scope:** A practical, time-boxed approach to designing a distinctive, credible, accessible dashboard for the UC Admissions Data Challenge. The local [challenge brief](../UC-Admissions-Data-Challenge.md) is treated as the product context; external links below are the evidence base.

## Executive synthesis

The dashboard should feel like a clear analytical argument, not a collection of attractive widgets. Its north star is:

> **Question → denominator → visual evidence → interaction → limitation.**

For this challenge, the strongest design is likely a calm, editorially structured analytical surface: one clear thesis, two or three primary views, a small set of purposeful filters, and visible method/caveat text. This is consistent with Tableau’s guidance to establish the audience and purpose first, prioritize the most important view, limit the number of views, and use interactivity to support exploration. [Tableau: Best Practices for Effective Dashboards](https://help.tableau.com/current/pro/desktop/en-us/dashboards_best_practices.htm)

“Distinctive” should come from decisions grounded in the subject matter—UC campuses, school pipelines, policy-era breaks, and actual-versus-expected comparisons—not from decorative novelty. The current skills.sh ecosystem makes the same useful distinction: its `frontend-design` skill emphasizes a concrete subject, intentional typography/color/layout, and avoiding predictable layouts, while `web-design-guidelines` is framed as an audit skill covering design, accessibility, and UX. Treat those as workflow aids, not as replacements for WCAG or data-interpretation judgment. [skills.sh directory](https://www.skills.sh/), [frontend-design](https://www.skills.sh/anthropics/skills/frontend-design), [web-design-guidelines](https://www.skills.sh/vercel-labs/agent-skills/web-design-guidelines)

## 1. Start with the data contract, not the canvas

The brief describes aggregated school/year/campus data—not individual student records—and explicitly warns about redacted blanks, the non-additive `Universitywide` row, weighted-rate calculation, post-2021 admissions-policy changes, COVID-era effects, field coverage, and the separate ethnicity/discipline/major files. These are interface requirements, not footnotes.

Before styling, write a one-page data contract for every visible metric:

| Contract field | Example for this challenge |
| --- | --- |
| Question | “How did the aggregate UC admission rate change across the policy-era break?” |
| Population | California public high-school applicants represented in the selected rows |
| Grain | School × year × campus; state this directly in the methodology panel |
| Numerator / denominator | Admits / applicants; aggregate counts first, then calculate the rate |
| Unit | Count, percentage, percentage-point residual, or distribution—not a vague “score” |
| Missingness | “Redacted / unavailable,” never silently converted to zero |
| Comparison | Campus, year, county, or expected-rate peer comparison; define the baseline |
| Caveat | Descriptive association only; policy and COVID eras are confounders for trend interpretation |

Put a compact “Reading this view” line near each chart. A judge should not have to infer whether a percentage is a mean of school percentages, a pooled rate, a share of applicants, or a share of admits.

## 2. Anti-generic guardrails that improve the work

| Common failure mode | Replace it with |
| --- | --- |
| A 3×3 grid of identical rounded KPI cards | A hierarchy: one thesis, one primary chart, one comparison, one detail view |
| Oversized number with no denominator | A metric lockup: value, plain-language label, numerator/denominator, time/filter context |
| Purple/teal gradient used everywhere | Rich neutrals plus a constrained semantic palette; reserve accent color for the active question or anomaly |
| Decorative “01 / 02 / 03” labels | Labels that encode real structure: “Trend,” “Campus comparison,” “School residuals” |
| Every chart shown at once | Progressive disclosure: overview first, focused tabs or a detail drawer second |
| Hover-only meaning | Persistent labels or annotations, keyboard-accessible focus, and a “view data” table |
| A map because the data contains locations | Use a map only when spatial pattern is the question; otherwise a ranked county/school comparison is easier to read |
| Motion added after the design is finished | Use motion only to explain state change, selection, or spatial relationship; support reduced motion |

The `frontend-design` skill’s most useful anti-slop instruction is to ground the design in the subject and make structural devices encode something true. For a data dashboard, that means visual identity should emerge from the data story and the team’s analytical voice, not from arbitrary cards, gradients, or glass effects. [skills.sh: frontend-design](https://www.skills.sh/anthropics/skills/frontend-design)

## 3. Recommended visual system

### Hierarchy and composition

Use a page title that states the question or thesis rather than a generic “UC Admissions Dashboard.” Under it, show the scope in one line: selected years, campuses, population, and rate definition.

Recommended desktop composition:

1. **Header:** question-led title, scope line, source/method link.
2. **Control strip:** year, campus, geography, and school filters; a clear “Reset” action; an explicit selected-state summary.
3. **Primary view:** the chart that answers the main question, placed first and given the largest visual area.
4. **Supporting view:** a comparison or distribution that explains the primary pattern.
5. **Detail view:** school/campus table or actual-versus-expected analysis with count context.
6. **Interpretation rail:** a concise takeaway, limitation, and “how to read” note.

This follows Tableau’s recommendation to put the most important view in the upper-left scanning area and to keep the dashboard to roughly two or three views when possible. [Tableau: Best Practices for Effective Dashboards](https://help.tableau.com/current/pro/desktop/en-us/dashboards_best_practices.htm)

Use layout containers or a consistent CSS grid so alignment is structural rather than hand-tuned. Material 3’s canonical layouts—feed, list-detail, and supporting pane—are useful patterns for deciding whether the user is scanning many items, comparing a selected item with its context, or exploring a primary chart with supporting detail. [Material 3: Canonical layout examples](https://m3.material.io/foundations/layout/canonical-examples/overview)

### Spacing and density

Choose a small token scale and use it everywhere: for example, 4/8/16/24/32 px for detail, component padding, section gaps, and major separation. Do not use spacing as decoration; use proximity to show which label belongs to which value and which controls affect which chart.

Carbon explicitly treats spacing as a system of tokens and recommends multiples of two, four, and eight; its grid guidance also uses repeated gutters and vertical rhythm to create alignment. [Carbon: Spacing](https://carbondesignsystem.com/elements/spacing/overview/), [Carbon: 2x Grid](https://v10.carbondesignsystem.com/guidelines/2x-grid/overview/)

Practical defaults:

- One page gutter at desktop; a smaller but still generous gutter on compact screens.
- 16–24 px inside a chart panel; 24–32 px between major sections.
- Avoid forcing every panel to equal height if that creates empty space or shrinks the main chart.
- Keep chart plot areas larger than their chrome: title, legend, toolbar, and axis labels should support the data rather than compete with it.

### Typography

Use one primary type family and a small, explicit scale. A neutral system sans or a deliberate typeface is fine; the important choice is consistency, legibility, and a visible hierarchy. Use weight, size, and leading together rather than making every heading larger. Avoid thin text for small labels, and use tabular numerals for aligned counts and rates.

Apple’s HIG treats typography as a tool for legibility and hierarchy, recommends avoiding light weights when text is small, and cautions against mixing too many typefaces. Carbon likewise uses type tokens, calibrated sizes, weights, and leading to organize complex product information. [Apple HIG: Typography](https://developer.apple.com/design/human-interface-guidelines/typography), [Carbon: Typography](https://carbondesignsystem.com/elements/typography/overview/)

Suggested roles:

- **Question/title:** one strong size and weight; plain language.
- **Section title:** concise and stable across states.
- **Metric value:** large enough to scan, but never detached from its label and denominator.
- **Chart title:** qualitative and insight-oriented, such as “Admission rates diverged after 2021,” only when the data supports that claim.
- **Axis/legend text:** concise; spell out unfamiliar abbreviations.
- **Method/caveat text:** readable secondary text, not tiny gray legal copy.

WCAG 2.2 also requires that content survive user-applied text-spacing changes without loss of content or functionality; do not bake critical labels into images or rely on fixed-height containers that clip enlarged text. [WCAG 2.2, SC 1.4.12 Text Spacing](https://www.w3.org/TR/WCAG22/#text-spacing)

### Color

Define semantic roles before picking swatches:

- neutral background / surface / border / primary text / secondary text;
- one interaction accent;
- categorical colors for campuses or groups;
- sequential colors for low-to-high values;
- a diverging scale for residuals around zero;
- status colors only for actual status, warning, or error.

Do not let the same color mean “UC Berkeley,” “selected,” and “positive.” Apple recommends consistent color meanings and alternative indicators beyond color; WCAG 2.2 SC 1.4.1 requires that color not be the only visual means of conveying information. [Apple HIG: Color](https://developer.apple.com/design/human-interface-guidelines/color), [WCAG 2.2: Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)

For visualizations, Carbon distinguishes categorical palettes from sequential palettes and discourages using gradients to represent meaningful progression or divergence. Use a neutral midpoint for residuals, label the direction explicitly (“below expected” / “above expected”), and include a numeric scale. [Carbon: Color palettes](https://v10.carbondesignsystem.com/data-visualization/color-palettes/)

Accessibility floor:

- Normal text: at least 4.5:1 against its background.
- Large text: at least 3:1.
- UI component boundaries, focus indicators, and essential graphical objects: at least 3:1 against adjacent colors.
- Never use red/green alone for a state or comparison; add text, shape, position, pattern, or a direct label.

These are WCAG AA thresholds, not aesthetic suggestions. [WCAG 2.2: Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), [WCAG 2.2: Non-text Contrast](https://www.w3.org/TR/WCAG22/#non-text-contrast)

## 4. Visualization choices for this dataset

Start with the analytical task, then choose the mark. Carbon’s chart-type guidance begins with the purpose of the visualization; Tableau similarly recommends choosing the format that answers the question and connects to the main purpose. [Carbon: Chart types](https://carbondesignsystem.com/data-visualization/chart-types/), [Tableau: Data visualization tips](https://www.tableau.com/visualization/data-visualization-best-practices)

| UC question | Recommended primary visual | Required supporting context | Avoid |
| --- | --- | --- | --- |
| How did admission outcomes change over time? | Line chart of pooled applicants, admits, and calculated admission rate; optionally small multiples by campus | Mark 2020 and the post-fall-2021 policy break; show counts and missingness | Averaging school-level rates; implying causality from a before/after line |
| How do campuses compare? | Ranked horizontal bars or dot plot with admission rate and applicant count | Show the selected year/filter; use labels and a common scale | Unsorted rainbow bars; comparing rates without sample size |
| Which schools differ from expectation? | Actual-versus-expected scatter or ranked residual bars | Encode or list applicant count; explain expected-rate definition and coverage | Treating residual as a causal score or ranking tiny denominators as definitive |
| Where is the school pipeline concentrated? | Ranked bars or compact table by county/school | Show population and coverage; preserve “unknown/unmatched” as a category where relevant | A map that consumes space without adding spatial insight |
| How do race/ethnicity patterns differ? | Separate ethnicity view using the dedicated file | Define denominator and category treatment; include a limitation statement | Joining redacted school-level race counts; presenting group differences without context |
| What are discipline/major pathways? | Fall-2025 ranked bars or dot plot | Label “Fall 2025 snapshot,” and state this is not a trend | Adding a fake time axis or using a donut for many categories |

For every chart:

- Use a descriptive title that says what the chart reveals, not just the field names.
- Put units in titles/axes and format percentages consistently.
- Label directly when there are only a few series; use a legend only when necessary.
- Make tooltips repeat the x/y values plus relevant context such as campus, year, count, and denominator. Carbon recommends concise, qualitative titles, direct labels where practical, and tooltips that repeat the data point’s axis values and details. [Carbon: Chart anatomy](https://carbondesignsystem.com/data-visualization/chart-anatomy/), [Carbon: Legends](https://carbondesignsystem.com/data-visualization/legends/)
- Provide a “View data” table or equivalent text summary. A chart is an interpretation aid, not the only copy of the data.
- Use the simplest mark that preserves the comparison: position and length before area, angle, decorative shape, or 3D effects.

## 5. Interaction design that earns its complexity

Keep the interaction model small and predictable:

1. **Filters:** group related controls, use clear labels (“Campus,” not “campus_filter”), show the active selection, and provide Reset.
2. **Cross-highlighting:** selecting a campus, year, or school should highlight the same entity in related views; do not silently change every chart without a visible state explanation.
3. **Details:** selection opens or reveals a detail region; do not make a judge hunt through hover-only tooltips.
4. **Comparison:** support one focused comparison at a time, such as “selected campus vs UC aggregate” or “actual vs expected.”
5. **Loading and empty states:** state what is loading, distinguish “no matching rows” from “data unavailable,” and explain redaction rather than showing blank cards.
6. **Keyboard and focus:** every control has a keyboard equivalent, a visible focus state, and a logical reading order.

Material 3 describes interaction states as distinct visual states—enabled, disabled, hover, focused, pressed, and dragged—and recommends applying them consistently. WCAG requires keyboard-operable functionality and a visible, persistent focus indicator. [Material 3: States](https://m3.material.io/foundations/interaction/states/overview), [WCAG 2.2: Keyboard](https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html), [WCAG 2.2: Focus Visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible.html)

Interactive motion should clarify cause and destination: a selected row can gently emphasize its corresponding point; a detail pane can enter from the control that opened it. Avoid parallax, looping ambient motion, or animation that delays access to the data. Respect `prefers-reduced-motion`; WCAG identifies non-essential interaction-triggered motion as something users should be able to disable. [WCAG 2.2: Animation from Interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html)

Make pointer targets comfortably larger than the minimum where feasible. WCAG 2.2 SC 2.5.8 sets a 24×24 CSS-pixel minimum or equivalent spacing exceptions; filters, icon buttons, chart controls, and mobile row actions should be designed around that floor. [WCAG 2.2: Target Size (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)

## 6. Responsive behavior: recompose, do not merely shrink

Design three compositions from the start:

- **Expanded desktop:** primary chart and comparison side by side or in a supporting-pane layout; methodology can remain visible.
- **Compact tablet/laptop:** stack the supporting view beneath the primary chart; keep filters grouped and visible.
- **Phone:** one vertical narrative; move filters into an accessible drawer or disclosure; keep the title, scope, primary chart, takeaway, and data table usable without horizontal page scrolling.

Use CSS grid/flexbox and content-driven breakpoints. WCAG 2.2 SC 1.4.10 requires content to reflow without loss of information or functionality at a 320 CSS-pixel width, with an exception for content whose two-dimensional layout is essential, such as a data table or map. A horizontally scrollable table can be valid, but the surrounding page and each cell still need to remain usable. [WCAG 2.2: Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)

Tableau’s guidance is a useful operational reminder: author at the final display size, test the real screen, and create distinct device layouts when one composition cannot preserve the story. [Tableau: Size and Lay Out Your Dashboard](https://help.tableau.com/current/pro/desktop/en-us/dashboards_organize_floatingandtiled.htm)

Do not let responsive behavior:

- collapse labels into unexplained icons;
- remove the legend without a visible “View legend” mechanism;
- hide the denominator or caveat;
- turn a comparison into a color-only distinction;
- put a fixed-width chart inside a page that requires horizontal scrolling.

## 7. Accessibility and verification checklist

### Semantic and non-visual access

- Use native headings, `main`, `nav`, `section`, `button`, `label`, and table elements before adding ARIA.
- Preserve a logical DOM order: title/context → filters → primary chart → supporting evidence → details → sources/limitations.
- Give each chart a concise title and text summary; expose the underlying data table or a structured “view data” panel.
- Ensure filter changes announce the updated scope/status without moving focus unexpectedly.
- Do not make chart marks the only keyboard-accessible path to values.

Tableau’s accessible-dashboard guidance is especially relevant as a warning: dashboard titles, filters, legends, captions, and view-data surfaces can be accessible, while mark selection and tooltips within a view may not be. Build the alternative representation intentionally rather than assuming the chart library will provide it. [Tableau: Build Dashboards for Accessibility](https://help.tableau.com/current/pro/desktop/en-gb/accessibility_dashboards.htm)

### Visual and responsive checks

- Keyboard-only pass: Tab/Shift+Tab, Enter/Space, arrow keys where appropriate, Escape for drawers, no traps.
- Focus pass: focus is obvious on light/dark surfaces and remains visible.
- Contrast pass: text, controls, selected states, chart lines, and essential marks.
- Color-vision pass: temporarily remove hue; the comparison should still be understandable through labels, position, shape, or pattern.
- Zoom/text pass: test at 200% and 400%; set text spacing overrides where possible.
- Reflow pass: 1440, 1024, 768, 390, and a 320 CSS-pixel equivalent; inspect clipping, overlap, and horizontal page scrolling.
- Motion pass: `prefers-reduced-motion: reduce`; no essential information disappears with animation disabled.
- Presentation pass: test on the actual projector/display if possible; confirm chart labels remain readable at viewing distance.

W3C explicitly notes that automated tools cannot determine every contrast or color-use issue, especially when meaning depends on context, so automated checks must be paired with human review. [W3C: Accessibility Conformance Challenges](https://www.w3.org/TR/accessibility-conformance-challenges/)

### Data and story checks

- Recompute a few visible rates manually from displayed counts.
- Verify that rate aggregations pool counts before dividing.
- Verify redacted blanks remain nonzero-unknown, not zero.
- Confirm `Universitywide` is not visually presented as the sum of campus rows.
- Inspect joins and `.notna()` coverage before showing comparisons.
- Annotate the 2020 COVID context and post-fall-2021 SAT/ACT policy context where a trend could invite causal interpretation.
- Label fall-2025-only discipline and major charts as snapshots.
- Show source files, definitions, and limitations in the repo README and in the dashboard’s source/method panel.

## 8. A fast, repeatable build workflow

### Pass 1 — Frame the argument (20–30 minutes)

Write three candidate questions. For each, specify audience, population, numerator, denominator, comparison, likely caveat, and the single visual that could answer it. Select one primary story and one backup; do not attempt to make every hypothesis a top-level view.

### Pass 2 — Sketch the information architecture (15 minutes)

Draw the title, scope, controls, primary chart, supporting chart, detail table, takeaway, and limitations as boxes. Use real field names and approximate real labels. If the sketch cannot be understood without a verbal explanation, fix the hierarchy before coding.

### Pass 3 — Build the data shapes and tokens (20–30 minutes)

Create reusable helpers for pooled rates, residuals, missingness, formatting, and filter state. Define semantic color tokens, spacing tokens, type roles, chart title patterns, and empty/loading/error states. Keep source/methodology content adjacent to the view rather than in a forgotten footer.

### Pass 4 — Implement the primary path first (45–60 minutes)

Make the initial load tell the story with no interaction. Then add only the filters and cross-highlighting that help answer the selected question. Add a table or text summary before polish. Use real data early so long labels, redactions, skewed denominators, and campus names shape the layout.

### Pass 5 — Critique in three modes (20–30 minutes)

1. **Five-second read:** What is this about? What should I look at first?
2. **Thirty-second read:** Can I state the finding with the correct denominator and scope?
3. **Two-minute read:** Can I inspect a comparison, understand a caveat, and reach the underlying values?

Run the accessibility, responsive, interaction, and data checks above. Ask one teammate unfamiliar with the implementation to narrate what they think the dashboard says; confusion is evidence about hierarchy or labeling, not a user failure.

### Pass 6 — Presentation hardening (15 minutes)

Prepare a 30-second opening: question, population, denominator, visual finding, limitation. Confirm that the initial viewport is legible, the app works from a cold start, and the GitHub repository contains the source/data provenance and a reproducible launch command. Because the event is time-boxed and in-person, treat network independence and a tested local fallback as part of polish.

## 9. Minimal “definition of done” for the dashboard UI

- The first screen answers one explicit question.
- Every percentage has a visible unit and denominator context.
- The primary view is readable without hover and has a data/table alternative.
- Filters have visible state, keyboard access, reset behavior, and empty states.
- The visual system uses deliberate hierarchy, consistent spacing, restrained color, and one subject-grounded signature detail.
- The layout works at desktop, compact, and phone widths; the page reflows at 320 CSS pixels.
- Text, controls, focus, and essential chart graphics meet the relevant WCAG AA thresholds.
- Reduced motion is supported.
- The dashboard states its population, aggregation, missingness, source, and limitations.
- A human reviewer can reproduce the visible numbers and explain the story in under a minute.

## Sources and source-selection notes

Normative accessibility requirements were taken from W3C WCAG 2.2 and its Understanding documents. Apple HIG, Material 3, IBM Carbon, and Tableau were used as first-party design-system and visualization guidance. skills.sh was checked on 2026-08-30 for the current ecosystem snapshot and for workflow-oriented skills relevant to frontend distinctiveness and UI auditing; its popularity/install counts are volatile and should not be treated as evidence of quality. The local challenge brief supplies the UC-specific data constraints and event context.
