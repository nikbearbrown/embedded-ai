# DESIGN.md — Visual Constitution
*Brutalist D3 × Claude · Load on-demand before any Generate phase session that touches visual output.*
*Generated: May 2026 · Load status: on-demand (visual sessions only)*

---

## Governing principle

Every mark earns its presence by serving the communication question. The typography does the personality work; the color does not. One red. One canvas. Everything else is neutral until it has a reason to speak.

---

## Surfaces covered

| Surface | Files | Context |
|---|---|---|
| Book layout | chapter pages, long-form reading | Print-ready, 65ch measure |
| Chart pantry | `*.html` chart examples | Browser, standalone, dark-mode aware |
| Slide deck | 16:9 lecture templates | Keynote/Reveal, classroom projection |

---

## Color system

Six variables. This is the complete palette. Requests for additional colors go back to the human layer.

```css
--color-white:     #FFFFFF;   /* canvas — default background */
--color-ink:       #121212;   /* primary text, headings, axes */
--color-red:       #C8102E;   /* primary accent — NEU Red */
--color-secondary: #545454;   /* captions, axis labels, secondary text */
--color-border:    #D4D4D4;   /* hairlines, dividers, card borders */
--color-ochre:     #C8860E;   /* decorative highlight only — see rules below */
```

### Role rules

**White** is the canvas. Not off-white. Not cream. `#FFFFFF`.

**Ink** is the default for all body copy, headings, and structural marks. `#121212` rather than pure black — warmer, easier at long reading lengths, still AAA on white (18.0:1).

**Red** is the one active color. It signals: brand, emphasis, interactive state, the primary data series in any chart. It is never decorative. It never encodes negative or danger in data visualization contexts — red is brand, not state.

**Secondary** is for supporting text — captions, source lines, axis tick labels, footnotes. 7.5:1 on white. AAA. Use everywhere body copy would be too heavy.

**Border** is for hairlines only. 1px rules between sections, card borders, table dividers, axis lines. Never for text.

**Ochre** is the one warm note. Decorative highlights: marker-style underlines beneath pull quotes, callout box left-borders, figure label accents, chapter number ornaments. **Never for body text or UI labels.** Contrast ratio 3.1:1 — AA large only. It is a visual accent, not an information channel.

### Data visualization palette

When charts use these colors:

| Role | Token | Notes |
|---|---|---|
| Primary series | `--color-red` | Most important series only |
| Secondary series | `--color-ink` | Or `#404040` for softer contrast |
| Neutral series expansion | `#787878`, `#ADADAD` | Grays only |
| Sequential scale low | `#F0EBE3` | Near-white warm neutral |
| Sequential scale high | `--color-ink` | `#121212` |
| Chart background | `--color-white` | |
| Gridlines | `--color-border` at 60% opacity | |
| Primary text / labels | `--color-ink` | |
| Secondary text / axes | `--color-secondary` | |
| Callout / annotation accent | `--color-ochre` | Borders and underlines, not fill |

Red encodes the brand and the primary series. Red never encodes "danger," "negative," or "alert" in charts. Use `--color-secondary` or `--color-ink` for data-state indicators.

### Accessibility

| Pair | Ratio | Level |
|---|---|---|
| `--color-ink` on white | 18.0:1 | AAA |
| `--color-red` on white | 5.9:1 | AA |
| `--color-secondary` on white | 7.5:1 | AAA |
| `--color-ochre` on white | 3.1:1 | AA large only — decorative use only |

Simulate color-blind before publishing any chart. Protanopia and deuteranopia are the primary targets. The red-to-gray chart palette is color-blind safe; verify each chart individually.

### Dark mode

Triggered by `prefers-color-scheme: dark`. Chart pantry files must support it. Book layout and slides do not require it.

```css
@media (prefers-color-scheme: dark) {
  --color-white:     #111111;
  --color-ink:       #F0EBE3;
  --color-red:       #E8243A;   /* slightly lighter — same hue */
  --color-secondary: #A0978C;
  --color-border:    #2E2E2E;
  --color-ochre:     #D49A30;   /* slightly lighter */
}
```

---

## Typography

### Typeface stack

**Display — EB Garamond**
Classical Garamond revival. Old-style figures, warm proportions. Used for H1/H2, chapter titles, article titles, pull quotes, blockquotes, the lede paragraph of any chapter opening. Loaded as user-supplied font; Google Fonts `EB+Garamond` as fallback.

```css
font-family: 'EB Garamond', 'Garamond', Georgia, serif;
```

**Body — Inter**
Humanist sans. Reading text, UI labels, captions, form elements, everything that is not a heading or code. Loaded from Google Fonts.

```css
font-family: 'Inter', -apple-system, 'Helvetica Neue', sans-serif;
```

**Mono — JetBrains Mono**
All code samples, terminal output, data file contents, chart axis tick labels, numeric annotations in charts. Loaded from Google Fonts.

```css
font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
```

**Hand — Shadows Into Light**
User-supplied handwriting font. Used only for margin notes, sketched callouts, circled words in diagrams. Never for body text, UI labels, or buttons. CSS class: `.handnote`.

```css
font-family: 'Shadows Into Light', cursive;
```

### Type scale — book layout

| Role | Family | Size | Line-height | Weight | Notes |
|---|---|---|---|---|---|
| Chapter title (H1) | EB Garamond | 48px | 52px | 400 | Sentence case |
| Section header (H2) | EB Garamond | 36px | 42px | 400 | Sentence case |
| Subsection (H3) | Inter | 22px | 30px | 600 | Sentence case |
| Component header (H4) | Inter | 17px | 24px | 700 | Sentence case |
| Body | Inter | 17px | 28px | 400 | 65ch max-width |
| Lede / first paragraph | EB Garamond | 20px | 32px | 400 | First paragraph of chapter only |
| Pull quote | EB Garamond | 24px | 34px | 400 italic | Ochre left-border |
| Caption | Inter | 13px | 18px | 400 | `--color-secondary` |
| Source line | Inter | 11px | 16px | 400 | `--color-secondary`, all-caps |
| Code block | JetBrains Mono | 14px | 22px | 400 | 80ch max-width |
| Inline code | JetBrains Mono | 14px | inherit | 400 | `--color-secondary` background tint |
| Margin note | Shadows Into Light | 13px | 18px | 400 | `.handnote` class only |

Headings are regular weight (400 for EB Garamond, 600 for Inter H3). Bold is reserved for inline emphasis and H4+. No all-caps except source lines and eyebrow labels.

### Type scale — chart pantry (HTML files)

| Role | Family | Size | Notes |
|---|---|---|---|
| Chart title | Inter | 16px / 700 | In-chart, top-left |
| Chart subtitle | Inter | 13px / 400 | `--color-secondary`, below title |
| Axis tick labels | JetBrains Mono | 11px | `--color-secondary` |
| Axis title | Inter | 12px / 400 | `--color-secondary` |
| Data label / annotation | Inter | 12px | `--color-ink` |
| Tooltip | Inter | 13px | |
| Legend label | Inter | 12px | |

### Type scale — slide deck (16:9)

| Role | Family | Size | Notes |
|---|---|---|---|
| Slide title | EB Garamond | 52px | Sentence case |
| Section divider title | EB Garamond | 72px | Sentence case |
| Body / bullet | Inter | 28px | Max 5 lines per slide |
| Caption / source | Inter | 18px | `--color-secondary` |
| Code | JetBrains Mono | 22px | Dark background block |
| Eyebrow / label | Inter | 16px / 700 | All-caps, `--color-secondary` |

### Casing rules

Sentence case everywhere. Title Case only for proper nouns and official course/book titles. No ALL-CAPS except eyebrow labels (≤4 words, ≤16px). No exclamation marks in authored copy.

---

## Spacing and rhythm

Base unit: 4px. Eight-step scale:

```
4px   8px   12px   16px   24px   32px   48px   64px
```

Vertical rhythm in long-form text anchors on a 28px baseline (matching body line-height). Headings break the grid only at section boundaries. Chart margins follow:

```
default chart margins: top 48 / right 40 / bottom 56 / left 64
wide-label charts:     top 48 / right 40 / bottom 56 / left 160
slide deck charts:     top 32 / right 32 / bottom 48 / left 64
```

---

## Layout rules

**Book layout**
- Body text: 65ch max-width
- Code blocks: 80ch max-width
- Full-page charts and figures: no max-width constraint, but left-aligned to the text column
- No sticky headers
- Headers are static

**Chart pantry (HTML files)**
- Responsive to window resize via ResizeObserver or window event listener
- Charts fill the viewport with computed margins
- No fixed pixel widths

**Slide deck**
- 1920×1080, 16:9
- Safe zone: 80px inset all sides
- Single-column center for text-heavy slides
- Left-text / right-chart split for data slides

---

## Borders, radii, shadows

**Radii:**
- `--radius-sm: 4px` — code badges, small tags
- `--radius-md: 8px` — callout boxes, cards
- No fully-rounded pills. No `border-radius: 50%` on rectangular elements.

**Borders:**
- Hairlines: 1px solid `--color-border`
- Callout left-border: 3px solid `--color-ochre`
- Focus ring: 2px solid `--color-red`, 2px offset in white

**Shadows:**
- `--shadow-sm: 0 1px 2px rgb(18 18 18 / 0.06)`
- `--shadow-md: 0 6px 20px -6px rgb(18 18 18 / 0.14)`
- No blue-tinted shadows. No inner shadows. No stacked shadows.

---

## Animation

Used in chart pantry HTML files. Not in book layout or slides.

**Easing:** `cubic-bezier(0.2, 0.8, 0.2, 1)` — ease-out-quart. No bounce, no overshoot.

**Durations:**
- Hover state: 120ms
- State transition: 200ms
- Chart enter: 320ms (bars, lines, arcs)
- Tooltip: 150ms appear, 100ms disappear

Fades and small (4–8px) translates only. No scale-on-mount. No parallax. No scroll-jacking. All animations must be suppressed under `prefers-reduced-motion: reduce`.

---

## State system

| State | Treatment |
|---|---|
| Link hover | 2px underline, color stays |
| Button hover | Background darkens ~6% via `color-mix` |
| Active/pressed | `translateY(1px)`, background darkens further |
| Focus | 2px solid `--color-red`, 2px white offset |
| Disabled | 40% opacity, `cursor: not-allowed` |
| Chart element hover | Opacity to 1.0, others to 0.35 |

---

## Imagery

Black-and-white or warm duotone. No saturated photography. No stock imagery. Sketches and hand-drawn diagrams are part of the brand — they go in the `.handnote` register. Grain and film texture on photographs is appropriate. No glossy renders.

Image treatment for charts and figures: white background, `--color-border` 1px frame, `--radius-md` if decorative border is needed.

---

## What this system never does

- No gradients as decoration. Gradient overlays on photography for legibility are permitted.
- No glassmorphism. No neumorphism. No blurry backgrounds as motif.
- No bluish-purple anything.
- No rainbow color palettes in charts — red is brand, grays are neutrals, that is the series palette.
- No red for data alerts or negative values in charts.
- No emoji in authored copy.
- No fully-rounded pill buttons on rectangular content.
- No ochre text at body size.
- No font substitutions — do not swap Inter for system-ui, Arial, or Helvetica.
- No ALL-CAPS headings beyond eyebrow labels.
- No exclamation marks.
- No sticky headers.

---

## Design audit checklist

Run before any chart pantry file or designed page is accepted.

1. Canvas is `#FFFFFF` (or correct dark-mode value under `prefers-color-scheme: dark`)
2. No color used outside the six-variable palette
3. Ochre appears only in decorative roles — no text at body size
4. Red is used for brand/emphasis/primary series — not for data alerts
5. Proportional ink honored — bar charts have zero baseline; area charts have zero baseline
6. `d3.scaleSqrt()` used for bubble/symbol radius encoding
7. Equal-area projection used for geographic choropleth (`geoEqualEarth` or `geoAlbersUsa`)
8. EB Garamond for display headings; Inter for body; JetBrains Mono for code and axis ticks
9. Font sizes meet minimum: body ≥ 16px (book), axis ticks ≥ 11px (charts), slides ≥ 28px
10. ARIA `role="img"` and `aria-label` on every SVG; `<title>` and `<desc>` inside
11. Color-blind simulation run (protanopia + deuteranopia)
12. Dark-mode renders correctly where required (chart pantry files)
13. `prefers-reduced-motion` suppresses all animations
14. No 3D effects, no perspective distortions on chart elements
15. Annotation passes the removal test — every text element answers a question the reader has

---

*Source of authority: this file. When this file and any other specification conflict, this file wins.*
*Next reconciliation: before any new surface is added to the project.*
