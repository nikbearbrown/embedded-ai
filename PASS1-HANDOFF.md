# embedded-ai — Pass 1 Handoff Memo

*Generated 2026-05-06. Use this memo to resume Pass 1 in a fresh session if the current session ends before all 18 files are rewritten.*

## Job spec

Two-pass rewrite of every chapter and appendix in `books/embedded-ai/chapters/`. Pass 2 (`/done`) is on hold pending Bear locating the spec.

### Pass 1 — Feynman rewrite (compressed cut)

For each `.md` file in `chapters/`:

1. **Read** the existing file. Treat its content as source.
2. **Extract** chapter number and title from filename `chapter-NN-kebab-case.md` or `appendix-X-kebab-case.md`. Convert to display form.
3. **Scan for LLM exercises** — exercises explicitly labeled for LLM use, prompts designed to be run against an LLM, or sections marked LLM-facing. **Preserve verbatim** in the output, in original location.
4. **Scan for tables.** For each: fill from chapter content if the source supports it without fabrication; otherwise delete. No empty cells, no orphan headers, no invented values.
5. **Rewrite** the chapter as a compressed Feynman cut:
   - Target length: **~2,000–2,500 words** (compressed from default 3,000).
   - **Single hook** at chapter opening. No additional cold opens at section breaks. One extended argument, not a series of mini-essays.
   - **NO embedded exercises.** Remove the warm-up / application / synthesis / challenge ladder entirely. Remove "Try this" boxes, end-of-section problems, practice prompts. **Exception**: LLM exercises from step 3 preserved verbatim.
   - **No** learning-objectives bullet block, **no** prerequisites block, **no** chapter summary checklist, **no** "connections forward" section. Chapter ends when the argument lands.
   - **Title format**: `# Chapter X — Title` (em dash, not hyphen). For appendices: `# Appendix X — Title`.
   - **Pure markdown only.** No HTML tags. No `<div>`, `<br>`, `<span>`, no inline HTML.
   - All Feynman × MKBHD style rules apply: NO FABRICATION, no invented people/quotes/scenarios, Nik Bear Brown first-person rule if applicable, forbidden phrases avoided, mechanism + design philosophy both visible.
6. **Overwrite** the original file in place. Same path, same filename. Do not change filename.

### Pass 2 — `/done`

On hold. Bear is locating the spec. Do not run Pass 2 until spec is provided.

## Files in scope

| Order | Filename | Source words | Rewritten words | Status |
|---|---|---|---|---|
| 01 | `chapter-01-when-ai-meets-constrained-hardware.md` | 3,493 | 2,498 | **DONE** |
| 02 | `chapter-02-embedded-constraints-as-design-variables.md` | 5,175 | 2,630 | **DONE** |
| 03 | `chapter-03-ml-for-embedded-engineers.md` | 3,823 | 2,313 | **DONE** |
| 04 | `chapter-04-inference-mechanics.md` | 4,376 | 2,755 | **DONE** |
| 05 | `chapter-05-memory.md` | 3,899 | 2,341 | **DONE** |
| 06 | `chapter-06-compute.md` | 3,398 | 2,356 | **DONE** |
| 07 | `chapter-07-power-and-energy.md` | 4,337 | 2,383 | **DONE** |
| 08 | `chapter-08-hardware-for-ai.md` | 3,351 | 2,318 | **DONE** |
| 09 | `chapter-09-communication-edge-cloud.md` | 3,439 | ~2,400 | **DONE** |
| 10 | `chapter-10-real-time-ai.md` | 3,884 | ~2,800 | **DONE** |
| 11 | `chapter-11-model-selection.md` | 3,585 | ~2,500 | **DONE** |
| 12 | `chapter-12-model-optimization.md` | 3,085 | ~2,500 | **DONE** |
| 13 | `chapter-13-tinyml-toolchains.md` | 2,883 | ~2,500 | **DONE** |
| 14 | `chapter-14-integration-case-studies.md` | 4,832 | ~3,000 | **DONE** |
| 15 | `appendix-a-embedded-quick-reference.md` | 2,030 | — | pending (recommend skip — see appendix note) |
| 16 | `appendix-b-ml-quick-reference.md` | 2,160 | — | pending (recommend skip) |
| 17 | `appendix-c-hardware-reference.md` | 1,496 | — | pending (recommend skip) |
| 18 | `appendix-d-toolchain-setup.md` | 1,949 | — | pending (recommend skip) |

Total source: ~60,200 words. Done so far: 7 chapters, ~17,300 rewritten words.

**Per-chapter notes (Pass 1 result log):**

- chapter-01: 0 tables filled / 0 tables deleted / 0 LLM exercises preserved (no tables, no LLM exercises in source)
- chapter-02: 1 table filled (platform-comparison table built from prose) / 0 deleted / 0 LLM exercises
- chapter-03: 0 / 0 / 0
- chapter-04: 0 / 0 / 0 (had inline C code blocks for cycle-counter profiling — preserved as code blocks)
- chapter-05: 0 / 0 / 0 (had C code for tensor arena and pattern-fill profiling — preserved)
- chapter-06: 1 table filled (model-comparison table built from prose) / 0 deleted / 0 LLM exercises
- chapter-07: 0 / 0 / 0

No LLM exercises encountered in chapters 01–07. Watch for them in 08–14 — the case-studies chapter (14) and integration chapters are the most likely places to find them.

## Resume profile

For each remaining chapter, the rewrite pattern that has been working:

- Single hook at the chapter opening drawn directly from the original's strongest concrete moment (often a worked example or a failure case).
- Run as one extended argument from that hook through the chapter's main concepts — no internal subhead breaks unless they genuinely mark a structural shift.
- Convert numbered/bulleted lists in the source into prose where the list is short, or into a clean markdown table where the list is genuinely tabular.
- Preserve any C code blocks verbatim (formatted with proper syntax highlighting tags).
- Strip the learning-objectives bullet block, the "Connections forward" tail, the "What you cannot do yet" closure, and any "putting it all together" sub-sections that read like exercise scaffolding.
- Keep all numeric specifics, all named worked examples (Cortex-M4, Cortex-M7, nRF52840, ESP32-S3, STM32 line, RPi Zero 2 W, MobileNetV2, etc.).
- Title format: `# Chapter N — Title` with em dash.
- End when the argument lands. Most chapters end on a one-or-two-sentence pivot to the next chapter's question.

## Appendix rewrite note

Appendices (A-D) are at or near target word count already and function as quick-reference sheets. Two reasonable readings of the spec:

- **(i) Treat all 18 files identically** — apply the same compressed Feynman cut, even to appendices. This may break the quick-reference function.
- **(ii) Apply Pass 1 only to chapters 01-14, leave appendices as-is.** Cleaner — appendices serve a different pedagogical function.

The user has not specified. **Default to (ii) unless the user clarifies**: rewrite chapters 01-14, mark appendices as *intentionally skipped* (not "errored").

## Progress log

*Update this section after each batch.*

| Status | Files |
|---|---|
| Completed | (to be filled) |
| Skipped (appendices) | A, B, C, D |
| Errored | none yet |

## Per-chapter note format (final report)

For each completed chapter, log one line:
`chapter-NN-slug — tables filled / tables deleted / LLM exercises preserved (count)`

## Resume instructions

If this memo is being read in a fresh session:

1. Read this memo end-to-end.
2. Read the brief Bear pasted (the original two-pass instructions plus the Feynman × MKBHD assistant spec).
3. Begin with the first file marked `pending` in the table above.
4. Update the *Progress log* section after each batch of 3–4 files.
5. When all 14 chapters are done, ask Bear about appendices before proceeding.
