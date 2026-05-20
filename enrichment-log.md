# Enrichment log — embedded-ai

Run date: 2026-05-20.

## Final state

- **79 SVGs / 79 PNGs / 79 D3 HTML files** — 1:1:1
- **All 14 substantive chapters fully closed**: 0 unresolved markers anywhere
- **All 14 existing Wayback Machine sections preserved untouched** (Easley, Conway, Zadeh, Estrin, Wang, Allen, Landauer, Mead, Perlman, Liu, Pareto, Ziv, Wilson, Ashby)
- **All 14 chapters have a new `## Prompts` section** with one structural prompt per figure, inserted immediately before the existing Wayback Machine section

## Per-chapter

chapter-01-when-ai-meets-constrained-hardware.md — 0 tables, 5 SVGs, 5 D3 HTMLs, Wayback kept (Annie Easley)
chapter-02-embedded-constraints-as-design-variables.md — 0 tables, 6 SVGs, 6 D3 HTMLs, Wayback kept (Lynn Conway)
chapter-03-ml-for-embedded-engineers.md — 0 tables, 5 SVGs, 5 D3 HTMLs, Wayback kept (Lotfi Zadeh)
chapter-04-inference-mechanics.md — 0 tables, 5 SVGs, 5 D3 HTMLs, Wayback kept (Thelma Estrin)
chapter-05-memory.md — 0 tables, 6 SVGs, 6 D3 HTMLs, Wayback kept (An Wang)
chapter-06-compute.md — 0 tables, 6 SVGs, 6 D3 HTMLs, Wayback kept (Frances Allen)
chapter-07-power-and-energy.md — 0 tables, 6 SVGs, 6 D3 HTMLs, Wayback kept (Rolf Landauer)
chapter-08-hardware-for-ai.md — 0 tables, 6 SVGs, 6 D3 HTMLs, Wayback kept (Carver Mead)
chapter-09-communication-edge-cloud.md — 0 tables, 6 SVGs, 6 D3 HTMLs, Wayback kept (Radia Perlman)
chapter-10-real-time-ai.md — 0 tables, 5 SVGs, 5 D3 HTMLs, Wayback kept (C.L. Liu)
chapter-11-model-selection.md — 0 tables, 6 SVGs, 6 D3 HTMLs, Wayback kept (Vilfredo Pareto)
chapter-12-model-optimization.md — 0 tables, 6 SVGs, 6 D3 HTMLs, Wayback kept (Jacob Ziv)
chapter-13-tinyml-toolchains.md — 0 tables, 5 SVGs, 5 D3 HTMLs, Wayback kept (Sophie Wilson)
chapter-14-integration-case-studies.md — 0 tables, 6 SVGs, 6 D3 HTMLs, Wayback kept (W. Ross Ashby)

## Summary

Total chapters processed: 14
Total tables rendered: 0 (no TABLE markers existed)
Total SVG+PNG pairs generated: 79
Total D3 v7 HTML files generated: 79
Total Wayback Machine subjects added: 0 (all 14 already present, all kept per "skip if existing" override)

## Process

1. **Setup pass.** Installed sharp, copied `SCRIPTS/svg-to-png.mjs` and `brutalist/` (CLAUDE.md + DESIGN.md) from ai-for-graphs.
2. **Marker-insertion pass.** 14 parallel agents — one per chapter — inserted INFOGRAPHIC/CHART markers where visuals would genuinely earn their place. Each chapter received 5–6 markers. All clean — no clustering, all inline.
3. **Enrichment pass.** 14 parallel agents — one per chapter — generated SVG + D3 v7 HTML for each marker, replaced the marker comment with a markdown figure ref, and inserted a new `## Prompts` section immediately before the existing `## AI Wayback Machine` section.
4. **PNG pass.** `node SCRIPTS/svg-to-png.mjs` rasterized all 79 SVGs at 300dpi.

## Notes

- Same EB Garamond / no-base64 typography rule as prior books in this series
- Brutalist constitution copied from `../ai-for-graphs-a-practitioners-guide/brutalist/`
- Existing Wayback sections (chosen by the book's author) were a particularly strong set — pre-2000 / period-foundational pioneers in computing and embedded systems. They were preserved per Bear's "skip if existing" rule without exception.
- This was the first book in the series where all 14 enrichment agents succeeded in a single parallel wave without hitting the rate limit. Likely because chapters were short (120–227 lines), markers were few per chapter (5–6), and there were no tables to render.
- Portrait `.jpg` files referenced in Wayback sections are unchanged from the book's prior state; this enrichment did not generate them.
