# Running Project Plan — embedded-ai (expanded)

*Step 1 (Chapter Map) and Step 2 (4 project options, expanded with worked examples). Pause for selection before generating per-chapter LLM Exercise blocks in Step 3.*

---

## At-a-glance comparison

| Dimension | Opt 1: Decision Doc | Opt 2: Calculator | Opt 3: Pitch Deck | Opt 4: Python Toolkit |
|---|---|---|---|---|
| **Final artifact** | 8–12 pg `.md` | 14-tab `.xlsx` | 15–20 slide `.pptx` | pip-installable CLI |
| **Tool path** | Cowork (Markdown) | Cowork (xlsx skill) | Cowork (pptx skill) | Claude Code |
| **Coding required?** | None | None (formulas only) | None | Heavy (Python, pytest) |
| **Per-chapter time** | 30–45 min | 45–60 min | 30–45 min | 60–90 min |
| **Cognitive load** | Synthesis-heavy | Mechanics-heavy | Communication-heavy | Engineering-heavy |
| **Map to book** | Chapter 14 *is* this | Formulas of every chapter | Argument structure of every chapter | Function per chapter |
| **Best for** | Generalists, PMs, MS engineering | Quants, financial-engineering students | Founders, consultants, product folks | CS/SWE students who want code |
| **Worst for** | Students who need concrete tools | Students who hate spreadsheets | Students who want to build something runnable | Non-coders |
| **Grading** | Rubric on 9 sections | Auto-grade on test cases | Rubric on argument quality | Auto-grade on test suite |
| **Survives the course?** | Maybe (artifact) | Yes (reusable tool) | Maybe (reference) | Yes (open-source) |

---

## Step 1 — Chapter Map (unchanged from prior pass)

(Detailed chapter map preserved at the bottom of this file for reference; jumping to expanded options.)

---

## Step 2 — Project Options, expanded

### Option 1 — The Embedded AI Design Decision Document

**One-line:** Pick one application; build a single growing Markdown decision doc, one section per chapter, that lands by ch 14 as the artifact a senior engineer is asked to produce before a project gets funded.

#### What the artifact looks like over time

**End of chapter 1 (~200 words):**

> # Embedded AI Decision Doc: Wildlife Acoustic Sensor for Jaguar Range Mapping
>
> ## Application
> A solar-powered acoustic sensor deployed in the Belize jungle that classifies jaguar vocalizations from background noise and reports detections to a base station via LoRaWAN. Stakeholder: Panthera conservation NGO. The failure that triggered this project: the previous deployment used continuous audio streaming over cellular, which cost $400/sensor/year and exhausted batteries in 11 days.
>
> ## What's at stake
> 200 sensors deployed across 80 km². Each false negative is a missed observation of a critically endangered species. Each false positive is a researcher hike. Project budget: $80K total; ongoing operating cost target: $0.

**End of chapter 7 (~1,200 words). The same doc now contains:**

- Application + stakes (above)
- Constraint quantification: memory ≤ 256 KB SRAM / 1 MB flash, latency soft ≤ 10 s, average power ≤ 0.4 mW (90 days on a 2,000 mAh + small solar panel under jungle canopy)
- ML scope: keyword spotting class on 4-second windows; output classes are jaguar / other-mammal / bird / no-detection
- Profiling plan: cycle counter on Cortex-M4 with DWT register; preprocessing (MFCC) profiled separately from inference
- Memory section: 1D CNN on MFCC; estimated 80 KB weights, 30 KB activations, 20 KB scratch buffer; total 130 KB SRAM, fits with 126 KB margin
- Compute section: 8 M MACs at 64 MHz with CMSIS-NN ≈ 80 ms inference; well under 10 s
- Power section: at 30-second duty cycle, average current 0.6 mA; needs improvement to 0.5 mA; mitigation is to wake on RMS threshold rather than fixed interval

**End of chapter 14 (~10 pages, ~5,000 words):**

A complete decision doc with 9 numbered sections, three plotted diagrams (Pareto frontier, energy-balance graph, comms-cost graph), a comparison table of 3 candidate hardware platforms with rejection rationale, a model-selection table with the 5 candidate architectures profiled, an optimization sequence (PTQ → check → QAT if needed), a deployment plan (TFLite Micro on STM32L4R5, OpResolver listing 4 ops, calibration set described), a verification protocol (50 known-jaguar audio clips, on-device output compared against TFLite Python output), a risk register (5 risks: domain shift across rainy/dry seasons, microphone weathering, jaguar-vocalization scarcity in training data, LoRaWAN coverage holes, solar-panel jungle-canopy variance), and a closing "what would change my mind" + "still puzzling."

#### Cognitive load by chapter

Light (1, 3, 9, 13). Medium (2, 4, 5, 6, 8, 10, 11). Heavy (7 — first energy-balance equation; 12 — first compression sequence; 14 — full synthesis).

#### Sample LLM Exercise (Chapter 5 — Memory)

```
You are extending the Embedded AI Decision Doc at design-doc.md (already started in chapters 1–4).

Context I'll give you: my application is [DESCRIBE APPLICATION IN 2-3 SENTENCES]. From chapter 2's constraint section, my SRAM budget is [N KB] and my flash budget is [N MB]. From chapter 3's ML-scope section, my candidate model class is [e.g., 1D CNN on MFCC for keyword spotting]. From chapter 4's profiling plan, my preprocessing is [e.g., MFCC over 4-second windows].

Add a Memory Section (Section 5) to design-doc.md that does the following, in this order:

1. Estimate weight memory in flash: parameter count × bytes-per-parameter at the target precision (int8 for embedded). Show the calculation.
2. Estimate activation memory in SRAM: identify the layer with the largest activation tensor and compute its size; this is usually the bottleneck for streaming inference.
3. Estimate scratch buffer for im2col or equivalent if the model uses convolutions; this is often 30-100% of the largest activation.
4. Sum the three for total SRAM requirement; compare against the budget; report margin.
5. If margin is below 20%, propose two mitigations from chapter 5's repertoire (buffer reuse, in-place computation, smaller model variant) and estimate the savings.
6. Close the section with one sentence on what would invalidate this estimate (e.g., "if measured activation memory exceeds prediction by more than 15%, the layer-by-layer estimate is wrong and I need to profile the actual TFLite tensor arena").

Output: append a new ## Section 5 — Memory Budget block to design-doc.md. Keep the prose tight; numbers in tables; show calculations.
```

**Tool:** Cowork edits design-doc.md in place. Could optionally graduate to a Claude Project for cross-chapter persistent context.

#### Failure mode

The project fails when the learner picks an application too vague to constrain. "Smart home device" produces a generic doc; "low-power dust sensor for clean-room manufacturing with 30-day battery target and 5-second latency" produces a sharp one. The first chapter must include a ruthless application-narrowing exercise.

#### Adaptability examples

- **Finance student:** "Smart credit-card with embedded fraud-detection model that flags suspicious transactions before authorization signal is sent."
- **Branding/marketing student:** "In-store retail sensor that classifies shopper engagement (high / medium / low) from anonymous overhead camera footage, no cloud transmission."
- **Wildlife biologist:** the jaguar example above.
- **Factory engineer:** "Predictive-maintenance sensor for CNC spindle vibration, 18-month battery, no cloud connectivity."
- **Healthcare student:** "Wearable insulin-pump-trigger predictor for type 1 diabetes, FDA Class II."

---

### Option 2 — The Constraint Calculator (parameterized .xlsx)

**One-line:** Build a multi-tab spreadsheet that takes application requirements in and emits feasibility verdicts, hardware shortlists, and optimization plans out. Each chapter adds a tab.

#### What the artifact looks like over time

**End of chapter 1:**

A single `Application` tab with input cells for: application name, stakeholder, latency target (ms or s, real-time class), accuracy floor (%), memory budget (flash KB, SRAM KB), power budget (mW average), BOM ceiling ($). Output cells empty until chapter 2.

**End of chapter 7:**

7 tabs: `Application`, `Constraints` (formulas converting requirements into the four-constraint framework), `ML_Scope` (input model class, parameters, MACs, activation sketch), `Profiling_Plan` (cycle-counter scaffold + checklist), `Memory` (flash + SRAM fit calculation with conditional formatting — green if margin >20%, yellow 5–20%, red <5%), `Compute` (MACs ÷ throughput estimate per processor class lookup table), `Power` (active + sleep + duty-cycle calculation, battery-life output).

**End of chapter 14:**

14 tabs. The `Summary` tab pulls binding-constraint detection across all the others — it auto-identifies which axis is tightest and says so in plain English ("Power is your binding constraint at 87% of budget"). The `Hardware_Shortlist` tab has a lookup of ~12 candidate microcontrollers with their key parameters (sleep current, active current, SRAM, flash, ARM core, accelerator support) and auto-eliminates those that fail any constraint, with the eliminated rationale visible. The `Model_Comparison` tab takes up to 6 candidate models as rows and computes Pareto-frontier membership. The `Optimization_Plan` tab predicts accuracy after PTQ and after QAT, predicts memory savings from N% structured pruning, predicts accuracy floor.

#### Cognitive load by chapter

Steeper at first because the learner is also learning spreadsheet patterns (named ranges, lookups, conditional formatting). After chapter 4 the learner is mostly extending established patterns.

#### Sample LLM Exercise (Chapter 5 — Memory)

```
You are extending constraint-calculator.xlsx (already has tabs Application, Constraints, ML_Scope, Profiling_Plan from chapters 1–4).

Add a new tab named Memory.

Inputs (drawn from existing tabs via cell references):
- Cell B2: parameter count (from ML_Scope!B5)
- Cell B3: bytes per parameter (1 for int8, 4 for float32; default 1)
- Cell B4: largest-activation-tensor size in elements (from ML_Scope!B7)
- Cell B5: scratch-buffer overhead percentage (default 50%)
- Cell B6: flash budget KB (from Constraints!C2)
- Cell B7: SRAM budget KB (from Constraints!C3)

Computed outputs:
- B10: weight memory KB = B2 * B3 / 1024
- B11: activation memory KB = B4 * B3 / 1024
- B12: scratch buffer KB = B11 * B5
- B13: total SRAM required KB = B11 + B12
- B14: flash margin = (B6 - B10) / B6, formatted as percent
- B15: SRAM margin = (B7 - B13) / B7, formatted as percent
- B16: feasibility verdict — "FITS" if both margins > 5%; "TIGHT" if either between 0–5%; "FAILS" if either < 0%

Conditional formatting:
- B14, B15: green if > 20%, yellow 5–20%, red < 5%

Below the calculation block, add a Mitigations section (rows 20–30) that lists three potential mitigations with their estimated savings (buffer reuse: 20–40% activation reduction; quantization float32 → int8: 75% weight reduction; smaller MobileNet width multiplier 1.0 → 0.35: 65% weight reduction).

Output: a complete Memory tab in constraint-calculator.xlsx with the formulas, the formatting, and a one-cell summary that the Summary tab can read.
```

**Tool:** Cowork (xlsx skill installed). The xlsx skill handles formulas, named ranges, conditional formatting, sheet linking.

#### Failure mode

The spreadsheet becomes unreadable if the learner doesn't enforce naming conventions early. The first-chapter prompt must include a rigid naming standard (`Constraints!flash_budget_kb`, not `Sheet2!B5`).

#### Adaptability examples

Same applications as Option 1, but the artifact is a tool, not a doc. A learner with three different applications can run them all through the same calculator and get three different verdicts.

---

### Option 3 — The Embedded AI Pitch Deck

**One-line:** Build the design-review deck a senior engineer would present to product leadership. One slide per chapter (mostly), plus speaker notes that justify every choice with the chapter's framework.

#### What the artifact looks like over time

**End of chapter 1:** 2 slides — Cover (project name, owner, date) and Problem Statement (what failed, what's at stake, what we're building).

**End of chapter 7:** 7 slides plus a closing-placeholder slide. The deck now tells a coherent argument up through the power budget. Speaker notes for the Power slide read like: *"Battery life is set by the average current. Active current during inference is 12 mA at 64 MHz; sleep current is 1.5 µA. With our 30-second duty cycle and 80 ms inference, average current is 0.55 mA, just over the 0.5 mA budget. We close that gap with a wake-on-RMS-threshold preprocessor that reduces inference frequency to roughly 10× per minute under typical conditions."*

**End of chapter 14:** A complete 18-slide design review deck with:

1. Cover
2. Problem statement
3. Constraints (the four numbers)
4. ML approach
5. Profiling strategy
6. Memory budget
7. Compute budget
8. Power and battery life
9. Hardware shortlist (3-platform comparison)
10. Edge-cloud architecture
11. Real-time and safety
12. Model selection (Pareto frontier diagram)
13. Optimization plan
14. Deployment toolchain
15. Validation results
16. Risk register
17. BOM and timeline
18. Closing ask

Every slide has speaker notes. The cover, problem, and closing slides are tuned to the audience the learner picks (investors / executives / regulators / product team).

#### Cognitive load by chapter

The hard part is not the content — it's the compression. Each chapter's ~2,500 words have to become one slide of bullets plus 60–90 seconds of speaker notes. That's harder than it sounds and is *the* skill for engineers heading toward leadership.

#### Sample LLM Exercise (Chapter 5 — Memory)

```
You are extending design-review.pptx (already has 4 slides from chapters 1–4).

Add a new slide titled "Memory Budget" in slot 5. Layout: title at top, three-column body, footer.

Body content:
- Left column titled "Budget": flash budget = [N MB], SRAM budget = [N KB]. Source cited as "STM32L4R5 datasheet."
- Middle column titled "Demand": predicted weight memory, predicted activation memory, predicted scratch buffer, total SRAM requirement. Each line labeled.
- Right column titled "Margin": flash margin %, SRAM margin %. Color-code: green > 20%, yellow 5–20%, red < 5%.

Speaker notes (60–90 seconds when read aloud):
1. State the verdict in one sentence (FITS / TIGHT / FAILS).
2. If TIGHT or FAILS, name two mitigations from chapter 5's repertoire and which one we picked.
3. Name one risk: what would make these numbers wrong (e.g., "the activation memory is a layer-by-layer estimate; if measured arena exceeds prediction by 15%, we go back and re-profile").

Use the design system from slide 1 (font: chosen by user; color palette: chosen by user). Match the visual rhythm of slides 2-4.

Output: an updated design-review.pptx with slide 5 added in the right slot, with speaker notes.
```

**Tool:** Cowork (pptx skill).

#### Failure mode

Pretty slides with empty arguments. The chapter-1 prompt must include a "no-decoration rule" — every visual element earns its place by carrying argument. This is the failure mode of every design-review deck in the wild.

#### Adaptability examples

- **Founder track:** the deck targets a Series A pitch — investors. Closing ask is funding.
- **Internal-product track:** the deck targets a product VP. Closing ask is roadmap commitment.
- **Regulatory track:** the deck targets an FDA submission committee. Closing ask is approval.
- **Consulting track:** the deck targets a client. Closing ask is project go-ahead.

---

### Option 4 — The TinyML Feasibility Toolkit (Python CLI)

**One-line:** A pip-installable Python package that takes a model file and a target spec and emits a feasibility report. Each chapter adds a module.

#### What the artifact looks like over time

**End of chapter 1:** Project scaffold: `pyproject.toml`, package skeleton at `src/tinyml_feasibility/`, a stub CLI (`tinyml-feasibility --help`), and one passing test in `tests/`. The CLI does nothing useful yet but installs cleanly.

**End of chapter 7:** 7 modules, each with tests:
- `application.py` (parse YAML application spec)
- `constraints.py` (typed Constraint objects)
- `model.py` (load .tflite, count params, count MACs)
- `profiling.py` (predict latency from MACs + processor class lookup)
- `memory.py` (compute flash + SRAM requirements + verdicts)
- `compute.py` (latency budget vs prediction)
- `power.py` (active + sleep + duty-cycle calculation, battery-life output)

A test suite of 30+ cases. The CLI now does:

```
$ tinyml-feasibility report --app jaguar.yaml --model jaguar_dscnn.tflite --target stm32l4r5

Application: Jaguar Acoustic Sensor
Target: STM32L4R5
==============================
Memory:        FITS  (flash 12% used, SRAM 51% used)
Compute:       FITS  (latency 80ms, budget 10000ms)
Power:         TIGHT (avg 0.55mA, budget 0.50mA — see mitigations)
Real-time:     N/A   (soft real-time)
==============================
Binding constraint: power
```

**End of chapter 14:** 14 modules + a `report.py` that emits Markdown matching the structure of Chapter 14's three case studies. The toolkit can:

```
$ tinyml-feasibility report --app vineyard.yaml --target rpi-zero-2w --model efficientnet-lite0.tflite --output vineyard-decision.md
```

…and produce a complete decision document. The toolkit replicates Chapter 14's three case studies as integration tests — given the YAML specs for industrial / medical / agricultural and the relevant model files, the toolkit produces the same architecture verdicts the chapter narrates.

#### Cognitive load by chapter

Steepest curve of the four. Requires Python, pytest, and a willingness to test-drive. The ceiling is also the highest — by chapter 14 the learner has shipped open-source software an embedded engineer can actually use.

#### Sample LLM Exercise (Chapter 5 — Memory)

```
Add a `memory` module to the tinyml-feasibility toolkit.

Goals:
1. Take a loaded model object (from `model.py`, exposes `param_count`, `largest_activation_size`, `precision_bytes`) and a target spec (from `target.py`, exposes `flash_kb`, `sram_kb`).
2. Return a `MemoryVerdict` dataclass with fields: weight_kb, activation_kb, scratch_kb, total_sram_kb, flash_margin_pct, sram_margin_pct, verdict (literal "FITS" | "TIGHT" | "FAILS"), mitigations (list of suggested mitigations if TIGHT or FAILS).

Implementation requirements:
- Use a pure function `assess_memory(model, target, scratch_overhead=0.5) -> MemoryVerdict`.
- Verdict logic: FITS if both flash_margin_pct > 20 and sram_margin_pct > 20; FAILS if either < 0; TIGHT otherwise.
- Mitigations come from a static dict mapping verdict reasons to mitigation lists ("activation_too_large" → ["buffer_reuse", "smaller_model_variant", "in_place_computation"]).
- Add `MemoryVerdict.to_markdown()` that emits the same shape as Chapter 14's memory section.

Tests (in tests/test_memory.py):
- A FITS case (large flash + SRAM)
- A TIGHT case (5% SRAM margin)
- A FAILS case (negative flash margin)
- An edge case at exactly 20% margin

Output: src/tinyml_feasibility/memory.py and tests/test_memory.py. Run pytest. All tests pass.
```

**Tool:** Claude Code (multi-file Python project, pytest, CI).

#### Failure mode

Learners without coding background bail in chapter 3. The recruiting filter is steep. Compensating: the toolkit is the only artifact the learner can reasonably show on a resume after the course.

#### Adaptability examples

- Every learner builds the same core toolkit; per-domain plugins differ.
- A robotics learner adds `motor_thermal_budget.py` as an extension module.
- An automotive learner adds `iso26262_asil_check.py`.
- A medical-devices learner adds `iec62304_check.py`.

---

## Decision questions for Bear

1. **What's the audience?** Generalists / PMs / managers → Option 1. Engineering students who'll build tools → Option 2 or 4. Communicators / founders / consultants → Option 3.
2. **Is coding required as a prerequisite?** If yes → Option 4 is on the table. If no → 1, 2, or 3.
3. **Does the artifact need to survive the course as a reusable thing the learner shows people?** Yes → Option 2 (calculator) or Option 4 (toolkit). The decision doc and pitch deck are usually one-offs.
4. **Where is the cognitive demand?** Synthesis (1) / mechanical-rigor (2) / argumentation (3) / engineering (4).
5. **How much instructor effort is grading?** Rubric-graded prose (1, 3) or auto-graded artifacts (2, 4).

If forced: **Option 1** for the most book-faithful and audience-broadest project. **Option 4** for a CS-track cohort. **Option 2** if you want students to leave with a tool. Avoid **Option 3** unless your cohort is heavy on communicators rather than builders.

---

## Step 1 — Chapter Map (full version, preserved)

(Same content as prior pass. Eliding in this view; full version remains in the file's history if you need it.)

Chapter 1: When AI Meets Constrained Hardware — four-constraint framework.
Chapter 2: Embedded Constraints as Design Variables — datasheet quantification.
Chapter 3: ML for Embedded Engineers — three-metric (params, MACs, activations) view.
Chapter 4: Inference Mechanics — four-stage pipeline, profiling.
Chapter 5: Memory — flash + SRAM, im2col, tensor arena.
Chapter 6: Compute — FLOPs / MACs / SIMD / WCET.
Chapter 7: Power and Energy — duty-cycling, race-to-sleep.
Chapter 8: Hardware for AI — DSP / NPU / FPGA / accelerator decision.
Chapter 9: Communication: Edge-Cloud — four tiers, four costs.
Chapter 10: Real-Time AI — soft/firm/hard, safety standards, design patterns.
Chapter 11: Selecting Models — Pareto frontier, deployment-aware metrics.
Chapter 12: Optimizing Models — quantization / pruning / distillation, prune→distill→quantize ordering.
Chapter 13: TinyML Toolchains — six-step pipeline, silent failures, verification.
Chapter 14: Integration Case Studies — three full case studies, binding-constraint pattern.

---

## Status — Step 3 complete

**Selected:** Option 4 — TinyML Feasibility Toolkit (Python CLI, Claude Code path).

**Per-chapter LLM Exercise blocks generated and inserted into chapter files:** all 14, in slot directly before the existing AI Wayback Machine block. Order in every chapter file is now: chapter prose → LLM Exercise → AI Wayback Machine.

**Companion source files:** `exercises/chapter-01.md` through `exercises/chapter-14.md` preserved as the canonical reference for the exercise blocks.

**Module map per chapter (what the toolkit gains each chapter):**

| Ch | Module added | Outputs |
|---|---|---|
| 1 | `application.py`, CLI scaffold | `Application` dataclass, `check-app` CLI |
| 2 | `target.py`, `constraints.py` | `Target` dataclass with datasheet catalog, `derive_constraints` translator |
| 3 | `model.py` | TFLite/ONNX loader, parameter count, MAC count, largest activation |
| 4 | `profiling.py` | 4-stage `LatencyEstimate` with bottleneck flag |
| 5 | `memory.py` | `MemoryVerdict` (FITS/TIGHT/FAILS) with mitigations |
| 6 | `compute.py` | `ComputeVerdict` with upgrade path |
| 7 | `power.py` | `PowerVerdict` with battery-life prediction |
| 8 | `accelerator.py` | NPU cost-benefit decision |
| 9 | `comms.py` | Per-tier `CommsCost` + `TierRecommendation` |
| 10 | `realtime.py` | Real-time class + design-pattern recommendation |
| 11 | `compare.py` | Multi-model `ParetoFrontier` |
| 12 | `optimize.py` | `OptimizationPlan` with prune→distill→quantize sequencing |
| 13 | `deploy.py` | TFLite conversion + verification report |
| 14 | `report.py` | Full `IntegrationReport` Markdown generator + 3 case-study integration tests |

**Capstone integration tests:** chapter 14's prompt mandates 3 integration tests that replicate Chapter 14's three case studies (industrial vibration / medical wearable / agricultural sensor) as `tinyml-feasibility report` invocations. The toolkit ships when those three tests pass — the framework, encoded as code, must reproduce the architecture verdicts the chapter narrates in prose.
