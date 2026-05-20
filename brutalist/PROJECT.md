# PROJECT.md — Brutalist D3 × Claude
*Phase Gate: both layers populated before Generate begins. Load alongside CLAUDE.md every session.*
*Generated: May 2026 · Stack: D3 v7 + single-file HTML/SVG*

---

## Layer 1 — Intent

**What this project is.**
A textbook teaching data visualization graphicacy through D3 v7 and Claude Code. Every chart in the pantry is a working, audited, publication-ready HTML file. The reader can paste one prompt into Claude Code and have a working chart of any type in seconds — then replace the data with their own.

**What a reader should understand after using it.**
That the design layer — which channel, which form, which baseline rule — is the hard layer. Claude Code handles syntax. The reader handles judgment. The specification is the work.

**The question this project answers.**
Given a dataset and a communication goal, what is the correct chart and how do I specify it precisely enough that Claude Code produces it right on the first attempt?

**The question it refuses to answer.**
Which chart looks most impressive. Aesthetics are a consequence of correct encoding, not a goal.

**Tone.** Editorial. Skeptical. Unsparing. Every mark earns its presence by serving the communication question.

---

## Layer 2 — The Decision Pipeline

*Distilled from the book. Apply in sequence. Do not skip steps.*

### Before writing any prompt

1. **Name the reader's question** (not the analyst's). One sentence.
2. **"Compared with what?"** Name the explicit comparison. If you can't, the chart isn't ready.
3. **Identify the chart family** using the FT Visual Vocabulary: comparison / change over time / distribution / relationship / part-to-whole / hierarchy / flow / spatial.
4. **Decompose the channels**: marks, then channel-to-attribute for each. Magnitude channels (position, length, area, luminance) for quantitative. Identity channels (hue, shape) for categorical.

### Writing the prompt (four moves, always)

| Move | Content |
|---|---|
| **Show** | Data shape: rows, columns, types, a 3-row sample |
| **Say** | Chart type named explicitly. D3 v7. Single HTML file, inline CDN. |
| **Constrain** | Every channel-to-attribute mapping. Sort order. Zero baseline if bars. Scale function if bubbles. Projection if geographic. Margins. Dark mode. |
| **Verify** | "Restate the channel decomposition. Comment each line. List unspecified decisions." |

### Hard encoding rules

- **Bar / area charts:** zero baseline. Non-negotiable. `domain([0, max])`.
- **Bubble / symbol radius:** `d3.scaleSqrt()`. Never `d3.scaleLinear()`.
- **Choropleth projection:** `d3.geoEqualEarth()` (world) or `d3.geoAlbersUsa()` (US). Never Mercator.
- **Heatmap color scale:** sequential (unipolar data) or diverging (meaningful midpoint). Never rainbow.
- **Stacked area:** most stable series at bottom. Zero baseline on the bottom layer.
- **Line chart:** y-axis range is a design choice, not a proportional-ink obligation. Point position is the channel, not area.
- **Pie chart:** five slices maximum. Past five, sort descending and aggregate remainder as "Other" — or switch to a horizontal bar chart.
- **Box plot whiskers:** Tukey's 1.5×IQR rule. Not min/max.

### The three D3 v7 failure modes

| Failure | Symptom | Fix |
|---|---|---|
| API hallucination | Runtime error on a d3.* call | Specify version; check CDN reference; run before accepting |
| Chart-type mismatch | Technically valid, wrong question | Name the chart type in Move 2 |
| Channel mismatch | Hue on quantitative, luminance on categorical | Specify every mapping in Move 3 |

### Audit before publishing (Evergreen/Emery — five categories)

- **Text:** title names the finding, not the occasion. Axes labeled with units. Comparison named explicitly.
- **Arrangement:** sorted by value. Space efficient. Reading order matches visual flow.
- **Color:** purposeful — encodes a specific attribute. Palette type matches data type. Color-blind safe. Dark mode specified.
- **Lines:** light gridlines at ticks only. No 3D effects. No perspective. Consistent stroke widths.
- **Overall:** every element passes Few's test ("does this support the message?"). Proportional ink maintained. ARIA role + aria-labelledby + `<title>` + `<desc>` on every SVG.

### Cairo's purpose test (run last)

After the audit passes: *can a reader from the target audience answer the question the chart was supposed to answer in five seconds?* If no, the chart has failed regardless of the audit score.

---

## Output inventory

| ID | File | Status | Notes |
|---|---|---|---|
| P01–P61 | `pantry/*.html` | in-progress | 61 chart types; see pantry directory |

---

*The code is generated against the schema. The schema is built by the human. The human decides what ships.*
