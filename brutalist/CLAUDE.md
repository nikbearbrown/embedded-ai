# CLAUDE.md — D3 v7 Coding Constitution
*One per stack. Changes when the renderer or framework changes, not per project.*
*Generated: May 2026 · Stack: D3 v7 + single-file HTML/SVG · Output: standalone browser-runnable HTML*

---

## Stack

- **Renderer:** D3 v7 (current release 7.9.0)
- **Output format:** Single self-contained `.html` file — inline CSS, inline JS, D3 loaded from CDN
- **Runtime:** Modern browser, no build step, no Node dependency
- **Data loading:** `d3.json()` relative path with inline fallback literal if fetch fails

### Pinned CDN URL

```html
<!-- UMD bundle — use this for all single-file HTML output -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
```

Do not substitute jsDelivr, d3js.org, or any other CDN without explicit instruction.
Do not use the ESM bundle (`+esm`) for single-file HTML output — it requires `type="module"` and
makes inline fallback data loading harder to reason about.

---

## Naming conventions

| Object | Convention | Example |
|---|---|---|
| Scale functions | camelCase, type-prefixed | `xScaleBand`, `yScaleLinear`, `rScaleSqrt`, `colorScaleSequential` |
| Axis generators | direction-prefixed | `xAxis`, `yAxis`, `xAxisTop` |
| SVG root | `svg` | `const svg = d3.select(...)` |
| Inner chart group | `gChart` | `const gChart = svg.append('g').attr('class', 'g-chart')` |
| Functional groups | `g` prefix, kebab-case class | `gBars`, `gAxes`, `gGridlines`, `gAnnotations`, `gLegend` |
| Data variables | camelCase plural | `barData`, `timeSeriesData`, `nodeData` |
| Tooltip div | `tooltip` | `const tooltip = d3.select('body').append('div').attr('class', 'tooltip')` |
| Margin object | `margin` | `const margin = { top, right, bottom, left }` |
| Computed dimensions | `chartWidth`, `chartHeight` | After subtracting margins from container |
| CSS classes on SVG elements | kebab-case | `.bar-rect`, `.axis-label`, `.gridline`, `.data-point` |

---

## Core patterns

### HTML page structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chart Title</title>
  <style>
    /* CSS custom properties first, then layout, then component styles */
    :root {
      --color-white:     #FFFFFF;
      --color-ink:       #121212;
      --color-red:       #C8102E;
      --color-secondary: #545454;
      --color-border:    #D4D4D4;
      --color-ochre:     #C8860E;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --color-white:     #111111;
        --color-ink:       #F0EBE3;
        --color-red:       #E8243A;
        --color-secondary: #A0978C;
        --color-border:    #2E2E2E;
        --color-ochre:     #D49A30;
      }
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--color-white); color: var(--color-ink); }
    #chart { width: 100%; }
    .tooltip { position: absolute; pointer-events: none; opacity: 0; }
    @media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; } }
  </style>
</head>
<body>
  <div id="chart" role="main"></div>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
  <script>
    // all chart code here
  </script>
</body>
</html>
```

### Margin convention

```javascript
const margin = { top: 48, right: 40, bottom: 56, left: 64 };
const container = document.getElementById('chart');
const totalWidth  = container.clientWidth  || 800;
const totalHeight = container.clientHeight || 500;
const chartWidth  = totalWidth  - margin.left - margin.right;
const chartHeight = totalHeight - margin.top  - margin.bottom;

const svg = d3.select('#chart')
  .append('svg')
    .attr('width',  totalWidth)
    .attr('height', totalHeight)
    .attr('role',   'img')
    .attr('aria-labelledby', 'chart-title chart-desc');

svg.append('title').attr('id', 'chart-title').text('Chart title here');
svg.append('desc').attr('id', 'chart-desc').text('One-sentence description of what the chart shows.');

const gChart = svg.append('g')
  .attr('class', 'g-chart')
  .attr('transform', `translate(${margin.left},${margin.top})`);
```

### Data join (v7 canonical — `.join()`, not `.enter().append()`)

```javascript
// Simple join — enter only, static chart
gChart.selectAll('.bar-rect')
  .data(data)
  .join('rect')
    .attr('class', 'bar-rect')
    .attr('x', d => xScaleBand(d.category))
    .attr('y', d => yScaleLinear(d.value))
    .attr('width',  xScaleBand.bandwidth())
    .attr('height', d => chartHeight - yScaleLinear(d.value));

// Join with separate enter/update/exit — use when transitions or keyed updates are needed
gChart.selectAll('.bar-rect')
  .data(data, d => d.id)          // key function for object constancy
  .join(
    enter  => enter.append('rect').attr('class', 'bar-rect').attr('opacity', 0)
                   .call(el => el.transition().duration(320).attr('opacity', 1)),
    update => update.call(el => el.transition().duration(200)),
    exit   => exit.call(el => el.transition().duration(200).attr('opacity', 0).remove())
  )
  .attr('x', d => xScaleBand(d.category))
  .attr('y', d => yScaleLinear(d.value))
  .attr('width',  xScaleBand.bandwidth())
  .attr('height', d => chartHeight - yScaleLinear(d.value));
```

### Event handler signature (v7 — `event` is first argument)

```javascript
// CORRECT in v7
element.on('mouseover', function(event, d) { /* event is MouseEvent, d is datum */ });
element.on('click',     function(event, d) { /* d3.event does NOT exist in v7 */ });

// WRONG — d3.event was removed in v7; using it will throw a ReferenceError
element.on('mouseover', function(d, i)    { const e = d3.event; }); // ✗ broken
```

### Tooltip pattern

```javascript
const tooltip = d3.select('body')
  .append('div')
    .attr('class', 'tooltip')
    .style('position', 'absolute')
    .style('pointer-events', 'none')
    .style('opacity', 0);

function showTooltip(event, html) {
  tooltip
    .html(html)
    .style('left', (event.pageX + 12) + 'px')
    .style('top',  (event.pageY - 28) + 'px')
    .transition().duration(150).style('opacity', 1);
}

function moveTooltip(event) {
  tooltip
    .style('left', (event.pageX + 12) + 'px')
    .style('top',  (event.pageY - 28) + 'px');
}

function hideTooltip() {
  tooltip.transition().duration(100).style('opacity', 0);
}

element
  .on('mouseover', (event, d) => showTooltip(event, `<strong>${d.label}</strong>: ${d.value}`))
  .on('mousemove', moveTooltip)
  .on('mouseout',  hideTooltip);
```

### Responsive resize (redraw pattern — preferred over viewBox scaling)

```javascript
function draw() {
  d3.select('#chart').selectAll('*').remove();
  const w = document.getElementById('chart').clientWidth || 800;
  // ... rebuild chart with new width
}
draw();
const ro = new ResizeObserver(() => draw());
ro.observe(document.getElementById('chart'));
```

### Data loading with inline fallback

```javascript
const FALLBACK_DATA = [{ label: 'A', value: 10 }, { label: 'B', value: 20 }];

async function loadData() {
  try {
    return await d3.json('./chart-name/data.json');
  } catch {
    return FALLBACK_DATA;
  }
}
loadData().then(data => render(data));
```

---

## Scale reference

| Use case | Function | Notes |
|---|---|---|
| Categorical x or y | `d3.scaleBand()` | `.padding(0.15)` default; `.rangeRound()` for pixel snapping |
| Quantitative continuous | `d3.scaleLinear()` | Zero-baseline for bar/area — domain starts at `[0, max]` |
| Bubble/symbol radius | `d3.scaleSqrt()` | **Required** — encodes area, not radius |
| Sequential color | `d3.scaleSequential()` | With `d3.interpolate*` interpolator |
| Diverging color | `d3.scaleDiverging()` | Meaningful midpoint required |
| Ordinal color | `d3.scaleOrdinal()` | Categorical hues |
| Time x-axis | `d3.scaleUtc()` | Use UTC; `d3.scaleTime()` for local-time axes |
| Log axis | `d3.scaleLog()` | Domain must not include zero |

---

## What I must not touch without explicit instruction

1. **Color values** — use `var(--color-*)` CSS custom properties from DESIGN.md. Do not hardcode hex values.
2. **Font families** — use `'EB Garamond', Georgia, serif` / `'Inter', sans-serif` / `'JetBrains Mono', monospace` only.
3. **Scale type for bubble/symbol radius** — always `d3.scaleSqrt()`. Never `d3.scaleLinear()` for radius.
4. **Zero baseline for bar and area charts** — domain `[0, max]`, never `[min, max]` for these forms.
5. **Chart type** — never choose or substitute chart type; it comes from PROJECT.md Layer 1.
6. **Data transformations** not specified in PROJECT.md Layer 2 — surface the need, do not apply.
7. **Projection for geographic charts** — `d3.geoEqualEarth()` for world, `d3.geoAlbersUsa()` for US states. Never Mercator.
8. **Animation durations and easing** — use values from DESIGN.md. Default: `duration(200)`, `ease(d3.easeCubicOut)`.
9. **Tooltip content and styling** — structure comes from the prompt; do not invent fields or apply colors outside the palette.

---

## Accessibility requirements (WCAG AA)

Every SVG chart must include:

```html
<svg role="img" aria-labelledby="chart-title chart-desc" ...>
  <title id="chart-title">Short chart title</title>
  <desc  id="chart-desc">One sentence: what the chart shows and its key finding.</desc>
  ...
</svg>
```

Interactive elements (bars, dots, arcs that respond to hover/click) must include:
- `tabindex="0"` to be keyboard-reachable
- `aria-label="Category: value"` describing the datum
- `keydown` handler responding to Enter and Space (same action as click)

Decorative elements (gridlines, axis lines, tick marks) must have `aria-hidden="true"` if they are
SVG elements that a screen reader would otherwise announce.

Minimum contrast:
- Body text in SVG: 4.5:1 against background
- Axis tick labels and captions: 4.5:1
- Chart marks (bars, lines, dots): 3:1 against adjacent background

---

## Verification stack

Run in this order after every chart generation:

1. **Format check** — open in browser; does it render without console errors?
2. **CDN check** — confirm the script src is exactly the pinned URL above, not a different version or CDN.
3. **Zero baseline** — for bar and area charts: inspect the y-scale domain; confirm it starts at `0`.
4. **Radius encoding** — for bubble charts: confirm `d3.scaleSqrt()` is used, not `d3.scaleLinear()`.
5. **Event signature** — search for `.on(` calls; confirm all use `(event, d)` parameter order.
6. **Tooltip** — hover a data point; confirm tooltip appears, moves, and disappears correctly.
7. **Resize** — narrow the window; confirm the chart redraws without overflow or clipping.
8. **Dark mode** — switch OS to dark mode; confirm the CSS variables invert correctly.
9. **Reduced motion** — simulate `prefers-reduced-motion: reduce`; confirm transitions are suppressed.
10. **Accessibility** — inspect SVG for `role="img"`, `aria-labelledby`, `<title>`, `<desc>`.
