# Embedded AI — CLI Video Ideas ("X with Claude")

*Candidates for the `cli` builder (Onda terminal in, vox output out). All BUILD lane — this is a quantitative engineering book, so every candidate is "build/measure X with Claude Code." **Every output is a VIDEO** — a Manim / Remotion / d3 animation, or a slate you fill with motion — **never a static image**. Ordered by score.*

**Read the "Human supplies" line on every card.** It names the part **Claude/the CLI cannot do** — train a real model, flash hardware, measure latency or current — so you know the real work before approving. Many cards run **fully synthetic** (Claude animates the book's figures / generated data), and those make honest videos on their own; where a card says *only real data is authentic*, you supply the model / dataset / hardware capture.

**Two sources mined:** (1) the book's own running **"TinyML Feasibility Toolkit"** — a per-chapter Claude Code project, chapters 1–14 — each module is a ready-made build episode; (2) buildable prose concepts where *running it* beats *stating it*. Cards 1–8 are the strongest standalone builds; Card 14 is the whole toolkit as a series.

---

## Candidate 01 — The MobileNetV2-0.5 That Almost Fit
- Source: `chapters/12-chapter-model-optimization.md` (chapter spine)
- Lane: BUILD (Claude Code)
- Hook: The best model came out of selection, compiled for the STM32H7 — and missed by 100 KB of flash and 70 ms of latency. Watch three knobs close a gap nobody could close by picking a different chip.
- The artifact: a compression-journey calculator that tracks flash / SRAM / latency / accuracy across four states — FP32 → INT8 PTQ → +25% structured prune → +distill — each against its ceiling (2 MB, 1 MB, 250 ms, 88%).
- Prompt seed: `claude "write compression_journey.py: MobileNetV2-0.5 on STM32H7 (2MB flash, 1MB SRAM, 250ms). Steps: fp32 → int8 PTQ (75% weight cut) → +25% structured prune → +distill. Track flash/SRAM/latency/accuracy vs ceilings, print a 4-state table."`
- Read / check: int8 cuts weights 4 MB→1 MB (75%); prune drops params 1.5M→1.125M and latency 320→240 ms; distill adds ~0.8% (89.8→90.6) with no size change. Ship state: 1.725 MB flash, 240 ms, 90.6%.
- Human supplies (Claude can't): **nothing** — the calculator runs on the chapter's illustrative figures end to end, which is a fine video. For *measured* numbers instead of the book's, you supply a trained MobileNetV2-0.5 + the defect-detection validation set and actually run prune/fine-tune/distill/quantize (Claude can't train or fine-tune a real model).
- Output medium: **Manim** (the four budget bars — flash / SRAM / latency / accuracy — growing step by step across the four compression states, each against its ceiling line, ending on the ship state).
- The change: `claude "add a 5th column: what happens if you quantize BEFORE pruning"` — show the order-matters penalty.
- Teardown angle: pruning earned the *fit*, distillation earned the *margin*, quantization made all of it possible — and doing them out of order compounds error.
- Exclusions: no QAT-vs-PTQ training-time tangent, no per-channel-scale proof, no second architecture.
- Score: 9/10

## Candidate 02 — Watch int8 Rounding Mash Your Activations
- Source: `chapters/12-chapter-model-optimization.md` (§ Quantization)
- Lane: BUILD (Claude Code)
- Hook: Quantizing weights from -1.5 to 1.5 is harmless. Quantizing an activation from 0.001 to 0.01 destroys the signal — same 8 bits, opposite outcome. Why?
- The artifact: a quantizer that maps float32→int8 (`round(x/scale)+zp`) and animates the reconstruction for two tensors — a wide symmetric weight range and a narrow small-magnitude activation range under the same scale.
- Prompt seed: `claude "write quantize_demo.py: linear int8 quant (scale, zero_point). Case A weights in [-1.5,1.5], case B activations in [0.001,0.01]. Show what the rounding does to each."`
- Read / check: case A scale ≈ 0.0118, error ≈ 0.005 (harmless); case B many distinct floats collapse to ~2 integer levels — the "mash zone." Damage is where range is wide AND the small-magnitude part carries information.
- Human supplies (Claude can't): **nothing — fully synthetic** (Claude generates the arrays; the math is exact). Optional realism only: drop in a real activation-tensor dump from your model to animate it on your data.
- Output medium: **Manim** (the sine over [0.001,0.01] snapping onto the too-coarse int8 grid and collapsing to two crimson bars, with the weight staircase hugging its curve alongside for contrast).
- The change: `claude "add per-channel scales and re-run"` — show per-channel rescues the imbalanced case.
- Teardown angle: quantization doesn't fail where the range is wide; it fails where the informative part of the signal lives in the rounding step.
- Exclusions: no symmetric-vs-asymmetric full treatment, no SIMD speedup math, no calibration-set-size study.
- Score: 9/10

## Candidate 03 — Find the Pruning Cliff with Claude Code
- Source: `chapters/12-chapter-model-optimization.md` (§ Pruning)
- Lane: BUILD (Claude Code)
- Hook: Remove 20% of a network's channels and lose under 1% accuracy. Remove 70% and it falls off a cliff. The whole game is knowing where the cliff is.
- The artifact: an accuracy-vs-pruning-rate curve (0→90% channels removed) with the 20–40% embedded sweet spot and the >70% collapse zone.
- Prompt seed: `claude "write pruning_curve.py: accuracy vs % channels structurally pruned, 0-90%. Shape: ~flat to 20%, 2-4% loss by 40%, 5-10% by 60%, collapse past 70%. Mark the 20-40% sweet spot and the >70% cliff."`
- Read / check: slope near-flat through 20%, steepening through 40/60, vertical past 70%. Takeaway marker: past 60%, switch to distillation onto a smaller architecture, not more pruning.
- Human supplies (Claude can't): for the **illustrative** curve, nothing — the shape is the chapter's, and it teaches the lesson. For a **measured** curve (real points on YOUR model), you supply a model + dataset and run the prune→fine-tune→eval loop at each rate — that training is yours; Claude can't produce real accuracy numbers.
- Output medium: **Manim** (the operating point sweeping right along the pruning-rate axis, accuracy dropping off the cliff, the sweet-spot band and the collapse zone lighting up as it passes).
- The change: `claude "overlay unstructured pruning — same accuracy curve, but annotate that latency never moves"`.
- Teardown angle: papers measure unstructured pruning because the accuracy curve looks great; embedded hardware assumes dense GEMM, so only structured pruning buys latency.
- Exclusions: no L1-vs-ablation scoring detail, no fine-tuning schedule, no sparse-kernel deep dive.
- Score: 9/10

## Candidate 04 — The Roofline: Is Your Model Compute- or Memory-Bound?
- Source: `chapters/06-chapter-compute.md`
- Lane: BUILD (Claude Code)
- Hook: Two models with the same FLOP count run at wildly different speeds on the same chip. The roofline tells you which one the memory bus is strangling.
- The artifact: a roofline plot (arithmetic intensity x, attainable GFLOP/s y) with the memory-bandwidth slope, the compute ceiling, and the model's operating point on it.
- Prompt seed: `claude "write roofline.py: given a target's peak GFLOP/s and memory bandwidth, draw the roofline. Place a model at its arithmetic intensity (MACs/bytes moved) and label compute-bound vs memory-bound."`
- Read / check: ridge point = peak_flops / bandwidth; left of the ridge is memory-bound (more compute won't help), right is compute-bound. Verify the model's MAC/byte ratio lands where the chapter says.
- Human supplies (Claude can't): two **data inputs** only — the target's peak GFLOP/s and memory bandwidth (from the datasheet), and the model's MAC + byte counts (from the toolkit's model loader or a profiler). No hardware run needed; Claude animates once you paste those numbers.
- Output medium: **Manim** (the model's operating point sliding across the roofline ridge; the memory-bound and compute-bound regions light up as it crosses, then the int8 version's point shifts right).
- The change: `claude "add a second point for the int8 version — show intensity shift after quantization"`.
- Teardown angle: the roofline tells you which knob (faster memory vs more MACs) will actually move latency before you spend money on the wrong one.
- Exclusions: no cache-hierarchy modeling, no DMA detail, no per-layer breakdown.
- Score: 9/10

## Candidate 05 — Build a Battery-Life Predictor with Claude Code
- Source: `chapters/01-chapter-when-ai-meets-constrained-hardware.md` + `07-chapter-power-and-energy.md`
- Lane: BUILD (Claude Code)
- Hook: The model was accurate, the hardware worked, the firmware shipped — and the product died in the field because nobody multiplied two numbers before launch.
- The artifact: a predictor — inference time × frequency = duty cycle; duty cycle × active current + sleep floor = average current; capacity / average current = days.
- Prompt seed: `claude "write battery_life.py: inputs inference_ms, freq_hz, active_mA, sleep_uA, battery_mAh. Compute duty cycle, average current, days of life. Sweep frequency."`
- Read / check: average current is the time-weighted mix of a tall active pulse and a near-zero sleep floor; shrinking the period multiplies average power even though each inference is unchanged.
- Human supplies (Claude can't): the current numbers. **Datasheet estimates** (active mA, sleep µA) make an honest illustrative animation — fine for the video. For a *real* battery-life claim, you supply a **power-monitor capture** of the active current during inference (Claude can't measure hardware).
- Output medium: **Manim** (a current-vs-time strip with the inference pulse, the period visibly shrinking as the battery-life days tick down beside it).
- The change: `claude "add race-to-sleep: finish faster at higher clock, then idle — show when it wins"`.
- Teardown angle: what kills embedded-AI products is almost never accuracy; it's a duty-cycle number you can compute before writing firmware.
- Exclusions: no regulator-efficiency detail, no battery-chemistry survey, no datasheet dive.
- Score: 8/10

## Candidate 06 — A Battery Can Be Full and Still Crash Your Device
- Source: `chapters/02-chapter-embedded-constraints-as-design-variables.md`
- Lane: BUILD (Claude Code)
- Hook: The coin cell had most of its charge left, and the device browned out and rebooted anyway.
- The artifact: a brown-out simulator — a CR2032's internal resistance caps sustained current near 3 mA, so an inference burst above that sags the supply below the reset threshold.
- Prompt seed: `claude "write brownout.py: CR2032 (3V nominal, R_internal limiting ~3mA). Given an inference current pulse, model V = V_oc - I*R over time and the brown-out reset line."`
- Read / check: average power says how long it runs; peak power says whether it runs at all. Sag crosses the reset line only during the burst; a bulk cap would blunt it.
- Human supplies (Claude can't): **nothing for the simulation** (Claude models the cell + pulse — a legitimate teaching output). For an authentic clip, you supply an **oscilloscope capture** of the real supply sag to show alongside or instead.
- Output medium: **Manim** (the supply-voltage trace sagging past the brown-out line as the current spike fires, then flattening once a 100µF bulk cap is dropped in).
- The change: `claude "add a 100µF bulk cap and re-run — show the sag flatten"`.
- Teardown angle: two power questions hide under one word — energy (how long) and instantaneous delivery (whether at all). Datasheets quote the first; the field punishes the second.
- Exclusions: no internal-resistance circuit derivation, no cap-sizing formula, no chemistry comparison.
- Score: 8/10

## Candidate 07 — Structured vs Unstructured Pruning: Measure the Lie
- Source: `chapters/12-chapter-model-optimization.md` (§ Pruning)
- Lane: BUILD (Claude Code)
- Hook: 80% of the weights are zero and the model runs at exactly the same speed. Sparse on paper, dense in silicon.
- The artifact: a benchmark comparing unstructured vs structured pruning on storage, SRAM, and latency against a dense GEMM baseline.
- Prompt seed: `claude "write prune_benchmark.py: dense baseline vs 50% unstructured (scattered zeros, dense kernel) vs 50% structured (channels removed). Report storage, activation SRAM, MAC count for each."`
- Read / check: unstructured cuts storage only and leaves latency/SRAM unchanged on dense kernels; structured shrinks all three — because embedded frameworks (TFLite Micro, CMSIS-NN) ship dense GEMM, not sparse kernels.
- Human supplies (Claude can't): Claude derives MACs/storage analytically (fine for the video's argument). But the punchline — *sparse runs at dense speed* — is only **authentic with real on-target latency** for the sparse vs dense model, which you measure on the MCU.
- Output medium: **Manim** (the three metric bars — storage, SRAM, latency — animating for unstructured vs structured; latency visibly refuses to move for unstructured while all three drop for structured).
- The change: `claude "add a hypothetical sparse-kernel column — show what unstructured WOULD buy if the kernel existed"`.
- Teardown angle: the compression a benchmark rewards and the compression your MCU rewards are different metrics; optimize for the kernel you ship.
- Exclusions: no CSR/COO format tutorial, no accuracy-recovery loop.
- Score: 8/10

## Candidate 08 — Build a Latency Predictor with Claude Code
- Source: `chapters/04-chapter-inference-mechanics.md` (LLM Exercise: latency predictor)
- Lane: BUILD (Claude Code)
- Hook: "How fast is my model?" has four answers, and only their sum ships. Decompose it before you optimize the wrong stage.
- The artifact: a latency predictor decomposing inference into pipeline stages (weight load, compute/MACs, memory movement, overhead) and estimating each stage's wall-clock on a target.
- Prompt seed: `claude "write latency.py: given a model's MACs, weight bytes, activation bytes and a target's GFLOP/s + bandwidth + overhead, estimate per-stage time and total."`
- Read / check: which stage dominates depends on arithmetic intensity — a memory-bound model spends most of its time moving bytes, not multiplying. (Pairs with the roofline, Candidate 04.)
- Human supplies (Claude can't): the **data inputs** (model MACs/bytes + target GFLOP/s/bandwidth) — easy. The honest *validation* needs a **real measured latency** from the target (hardware); optional, but that's the check that proves the model isn't fiction.
- Output medium: **Manim** (the four pipeline-stage bars filling in sequence as the inference runs, the dominant stage highlighted; then the int8 re-run showing which stage shrinks).
- The change: `claude "re-run for the int8 model — show which stage shrinks"`.
- Teardown angle: optimizing the stage that isn't the bottleneck is the most common wasted week in embedded ML.
- Exclusions: no cycle-accurate simulation, no compiler-scheduling detail.
- Score: 8/10

## Candidate 09 — Build a Pareto Model-Selector with Claude Code
- Source: `chapters/11-chapter-model-selection.md` (LLM Exercise: Pareto comparison)
- Lane: BUILD (Claude Code)
- Hook: Benchmark accuracy lies to you. The leaderboard winner loses on your device — so plot the whole field and keep only the ones nothing beats on every axis.
- The artifact: a multi-model Pareto tool — score N candidates against the app's constraints (accuracy, latency, flash) and highlight the Pareto frontier.
- Prompt seed: `claude "write pareto.py: given N models with (accuracy, latency_ms, flash_kb), compute the Pareto frontier and mark it; grey out dominated models."`
- Read / check: a model is dominated if another beats it on every axis; the frontier is the only honest shortlist. The leaderboard winner is sometimes dominated once latency and flash enter.
- Human supplies (Claude can't): the **real (accuracy, latency, flash) row for each candidate model** — accuracy from your eval, latency and flash **measured on the target**. Claude builds the frontier tool but cannot produce the measurements; with illustrative numbers it teaches the method, with your numbers it makes the decision.
- Output medium: **Manim** (the model field appearing on the accuracy-vs-latency plane, dominated points greying out one by one, the Pareto frontier drawing itself through the survivors).
- The change: `claude "add a constraint mask — grey out anything over 250ms or 2MB before computing the frontier"`.
- Teardown angle: single-number benchmarks optimize for the leaderboard's constraints, not yours; the Pareto frontier is what selection actually is.
- Exclusions: no accuracy-metric philosophy, no dataset-shift discussion, no fourth axis.
- Score: 8/10

## Candidate 10 — Deploy a Keyword Spotter to a Nano 33 BLE Sense
- Source: `chapters/13-chapter-tinyml-toolchains.md` (LLM Exercise: deployment runner)
- Lane: BUILD (Claude Code)
- Hook: The model was 94% accurate in Python. After the toolchain got done with it, it was 91% — and the 3% vanished in a step nobody watched.
- The artifact: a deployment runner — wrap the TFLite int8 conversion, simulate on-target inference via the TFLite Python interpreter, and emit a report bisecting which layer/op leaked accuracy vs the float model.
- Prompt seed: `claude "write deploy_runner.py: convert a keras model to TFLite int8, run the TFLite interpreter on a val set, compare to the float model, and bisect which layer/op introduced the largest output divergence."`
- Read / check: toolchain-induced accuracy loss is a *separate* loss from quantization error; the bisection localizes it to a specific op (an unsupported fusion, a range mismatch), not "quantization in general."
- Human supplies (Claude can't): a **trained keyword-spotter model** (keras/TFLite) + a **validation set** — Claude can't train these. **Given those, Claude does the rest in pure Python** (conversion + interpreter sim + bisection — no hardware). Real on-device flashing on the actual Nano 33 is an optional extra you'd capture yourself.
- Output medium: **Manim** (the per-layer divergence bars rising as the bisection walks the network to the leaking op) — or a **screen-recording mp4** of the real CLI run if you want the authentic session.
- The change: `claude "add a per-op supported/unsupported check for CMSIS-NN and flag fallbacks"`.
- Teardown angle: the six-step deploy pipeline breaks silently between steps; the only defense is a diff at every hop.
- Exclusions: no Edge Impulse UI walkthrough, no ONNX-vendor-compiler survey, no flashing demo.
- Score: 8/10

## Candidate 11 — Distillation: See the Soft Label's Extra Signal
- Source: `chapters/12-chapter-model-optimization.md` (§ Distillation)
- Lane: BUILD (Claude Code)
- Hook: A one-hot label says "cat." The teacher says "85% cat, 5% dog, nothing else" — and that 5% is the part that trains a better student.
- The artifact: a distillation demo — teacher's softened distribution vs the one-hot label, and a temperature sweep flattening the distribution to expose the wrong-class relative probabilities.
- Prompt seed: `claude "write distill_demo.py: teacher logits for a 10-class 'cat' image. Compare the one-hot label vs softmax(logits/T) for T=1,3,6. Show mixed loss L = α·hard + (1-α)·soft and how T controls what transfers."`
- Read / check: higher T emphasizes the relative probabilities of the wrong classes — the transferable knowledge; a distilled student typically gains 2–5% over hard-label training alone.
- Human supplies (Claude can't): **nothing for the synthetic demo** (Claude sets illustrative teacher logits — teaches the idea fully). The **2–5% gain is only real if you actually distill** a student against a teacher on your dataset — that training run is yours.
- Output medium: **Manim** (the teacher's probability bars morphing as temperature rises, the one-hot label standing rigid alongside for contrast).
- The change: `claude "pair it with pruning: distill the pruned student against the float teacher, show accuracy clawed back"`.
- Teardown angle: the teacher's reasonable mistakes are the signal; hard labels discard exactly the information a small model most needs.
- Exclusions: no KL-divergence derivation, no full training loop, no dataset specifics.
- Score: 8/10

## Candidate 12 — Build a Memory Verdict Module with Claude Code
- Source: `chapters/05-chapter-memory.md` (LLM Exercise: memory.py)
- Lane: BUILD (Claude Code)
- Hook: Flash holds the weights; SRAM holds the activations; they fail for different reasons and a single "out of memory" hides which one.
- The artifact: the toolkit's first verdict module — compare a model's flash (weights + firmware) and SRAM (largest activation) against a target's budget and emit a typed verdict with mitigations.
- Prompt seed: `claude "write memory.py: inputs param_count, dtype, firmware_kb, largest_activation, target flash_kb + sram_kb. Emit Verdict(fits, flash_margin, sram_margin, mitigations[])."`
- Read / check: weight memory = params × bytes/param (int8 = 1); SRAM is driven by the *largest single* activation, not the sum. The verdict distinguishes a flash problem (compress weights) from an SRAM problem (tile/restructure).
- Human supplies (Claude can't): the **data inputs** only — the model's param count + largest-activation size (from the loader) and the target's flash/SRAM budget. No hardware, no training; Claude computes the verdict end to end once you give the numbers.
- Output medium: **Manim** (the flash + SRAM budget waterfalls filling against their ceiling lines, the typed verdict stamping in; the int8 toggle re-running to show flash pass while SRAM barely moves).
- The change: `claude "add int8 as a toggle and re-emit the verdict — watch flash pass, SRAM barely move"`.
- Teardown angle: "it doesn't fit" is two different bugs with two different fixes; a typed verdict forces you to name which.
- Exclusions: no linker-script detail, no double-buffering deep dive.
- Score: 7/10

## Candidate 13 — Build a Real-Time Verdict Module with Claude Code
- Source: `chapters/10-chapter-real-time-ai.md` (LLM Exercise: real-time verdict)
- Lane: BUILD (Claude Code)
- Hook: "Fast enough on average" is how safety-critical AI fails. The deadline you must never miss isn't the mean — it's the worst case.
- The artifact: a real-time verdict module — classify the deadline class (soft / firm / hard), check worst-case execution time (WCET) against the deadline, recommend a pattern when AI sits in a safety loop.
- Prompt seed: `claude "write realtime.py: inputs deadline_ms, deadline_class, measured_latencies[]. Compute WCET (tail, not mean), classify soft/firm/hard, emit verdict + pattern if in a hard loop."`
- Read / check: WCET is the tail of the latency distribution; a model that passes on mean latency can fail on WCET.
- Human supplies (Claude can't): the **measured latency distribution from the target** — an array of *real* inference times under load. WCET is a tail of real runs; Claude classifies and animates, but cannot invent authentic latencies. A synthetic distribution demonstrates the method; your measurements make the verdict real.
- Output medium: **Manim** (the latency histogram building bar by bar, the WCET tail extending past the deadline line, then jitter pushing the tail further over).
- The change: `claude "add jitter from a GC / DMA stall and show the tail blow past the deadline"`.
- Teardown angle: real-time isn't "fast," it's "bounded"; optimizing the average while ignoring the tail is the classic safety failure.
- Exclusions: no RTOS-scheduler theory, no priority-inversion tangent.
- Score: 7/10

## Candidate 14 — Series: Build the TinyML Feasibility Toolkit with Claude Code (Ch 1–14)
- Source: every chapter's `## LLM Exercise` (the book's running Claude Code project)
- Lane: BUILD (Claude Code) — **a 14-part series, one module per chapter**
- Hook: By the last chapter you've built a tool that reads a model + a target and tells you, with receipts, whether it will ship — every module a chapter, every chapter a CLI video.
- The artifact: the full arc — scaffold + Application spec (Ch1) → Target catalog + Constraints (Ch2) → model loader (Ch3) → latency predictor (Ch4) → memory verdict (Ch5) → compute verdict (Ch6) → power verdict (Ch7) → accelerator decision (Ch8) → comms-tier calculator (Ch9) → real-time verdict (Ch10) → Pareto selector (Ch11) → optimization recommender (Ch12) → deployment runner (Ch13) → integration report + tests (Ch14).
- Prompt seed: each episode opens with that chapter's exact exercise prompt; the OUTPUT beat is the new module running on a real model+target and printing its verdict.
- Read / check: each module's output is checkable against the chapter's worked case; the series payoff is the Ch14 integration report reproducing the three case studies (vibration monitor, medical wearable, ag disease detector).
- Human supplies (Claude can't): per module. The **inputs are mostly data** (model specs, target datasheet numbers) that Claude runs on directly. The modules whose honest output needs **real measurement** — latency (Ch4/6), current (Ch7), WCET (Ch10), on-target deploy (Ch13) — need your **hardware captures / a trained model** for authentic numbers; the rest run synthetically on the book's cases and still teach.
- Output medium: a **screen-recording mp4** of the CLI running + verdict output, with a short **Manim** budget/verdict animation per module. (Never a still — the terminal session and the animated verdict are both motion.)
- The change: each episode's CHANGE beat is the next chapter's module — the series is the iterate loop at book scale.
- Teardown angle: the toolkit is the book's real thesis — feasibility is a computation, not an opinion — and building it live is the most honest way to teach that.
- Exclusions: don't front-load all 14 into one video; one module per reel, each standing alone.
- Score: 9/10 (as a series); individual modules 7–8 on their own.

---

*Next: pick the cards you want (add to `vox/reels/QUEUE.md` or say `cli <card>`), and the `cli` builder turns each into an Onda-terminal reel with the output slot filled by the animation named above. Cards that run fully synthetic (02, 04, 06, 11, 12) can be built end-to-end today; the rest teach synthetically now and get more authentic once you supply the model / dataset / hardware capture named in "Human supplies." Every output is a video — Manim/Remotion/d3 or a slate, never a png.*
