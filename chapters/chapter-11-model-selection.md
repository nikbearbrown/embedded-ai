# Chapter 11 — Selecting Models for Constrained Deployment

You have three models on your desk, each trained on the same factory-defect dataset, each promising to do the job. The first is MobileNetV2 at 89% accuracy, 1.2 MB of flash, 180 KB of activation memory, 220 ms per inference on your STM32H7. Every constraint is met — barely. Flash sits at 60% of capacity, SRAM at 70%, latency 20 ms under the 240 ms budget. The second is EfficientNet-Lite0 at 91% accuracy, 1.8 MB of flash, 240 KB of SRAM, 280 ms per inference. More accurate. Violates flash, violates SRAM, violates latency. The third is a custom depthwise-separable CNN at 87% accuracy, 600 KB of flash, 90 KB of SRAM, 110 ms per inference. Comfortably inside every limit.

Which one do you ship?

The answer is not "the most accurate one," because the most accurate one does not run. The answer is not "the smallest one," because you may need 88% accuracy to pass acceptance testing. The answer depends on which constraint is binding, which threshold is mandatory, and how much margin you want for the next firmware update that adds a feature. There is no scoreboard answer to this question. There is only the answer that fits *this* device, *this* dataset, and *this* deadline.

Up to this chapter we treated the model as something handed to us, and asked whether it fit. Now we choose. Model selection is the first move of model-aware design — the move where you stop optimizing around a model and start optimizing for a target.

## Why benchmark accuracy lies to you

The machine-learning research community ranks models on standardized benchmarks. ImageNet top-1 for image classification. COCO mAP for object detection. WER for speech recognition. Papers get published and headlines get written when a number on one of these leaderboards moves up.

Those numbers are wonderful for tracking progress in research. They are nearly useless for choosing a model to deploy on a microcontroller.

Two reasons. The first is that benchmark accuracy is dominated by the wrong axes. A model with 95% ImageNet accuracy and 80 million parameters is not a candidate for a board with 1 MB of flash. The leaderboard tells you nothing about whether the model can run; it ranks models inside an unstated assumption of unlimited resources.

The second reason is the domain gap. ImageNet is 1.2 million high-resolution photographs of 1,000 object classes, taken in diverse settings with professional cameras. Your deployment is 96×96 grayscale frames from a $4 camera under a fluorescent strip light, classifying three kinds of stamping defect. The features that distinguish a Persian cat from a Burmese cat in ImageNet are not the features that distinguish a hairline crack from a tooling mark. A model trained on ImageNet typically loses 5–20% accuracy when transferred to a domain-specific task — sometimes more if the imaging conditions are unusual.

So the metrics that actually predict embedded deployment success are different from the metrics on the leaderboard. You need five.

**Latency on target hardware.** Not theoretical FLOPs, which predict CPU latency badly because they ignore memory traffic, cache behavior, and SIMD utilization. Not inference time on the GPU the paper used. Wall-clock milliseconds on your actual processor running your actual inference framework, with preprocessing and postprocessing included if they ship with the model. Run it 100 times and report the mean, the 95th percentile, and the maximum. The maximum is your empirical worst-case execution time.

**Memory footprint.** Not parameter count alone. Weight memory in flash plus activation memory in SRAM, both at the precision you actually deploy at — int8, not float32. The way you measure this is to compile the model into your firmware and read the linker map file, then read the tensor arena size that your inference framework reports.

**Energy per inference.** Measured on target with a current-sense resistor and an oscilloscope, integrated over the full inference cycle. For battery devices, also measure average power across realistic duty cycles, because the average is what determines whether the coin cell makes it to next quarter.

**Accuracy on your dataset.** Not ImageNet accuracy. Validation accuracy on data that matches your deployment distribution: same camera, same lighting, same noise. If you must use a pretrained model, fine-tune the final layers on your own data and evaluate there.

**Accuracy under quantization.** Never assume quantization is free. Measure validation accuracy at float32 and again at int8, on your dataset. If the gap is more than 3–5%, something is wrong — the calibration set is unrepresentative, or you have layers with weights too small to survive int8, or you have activations whose dynamic range spans four orders of magnitude. A model that takes a 12% accuracy hit going to int8 is not the model you measured at float32.

These are five empirical questions. None of them can be answered from a paper or a datasheet. You profile each candidate, on your hardware, with your data, before you choose.

## What makes an efficient architecture efficient

Once you accept that efficiency matters, you start asking what architectural choices buy efficiency. The answer is not "smaller everything." The answer is that some operations cost a lot less than others for almost the same expressive power, and that the architectures designed for embedded targets are the ones that figured out which operations to substitute.

The clearest example is depthwise separable convolution, the trick at the heart of MobileNet. A standard 3×3 convolution with C input channels and C output channels does 9C² multiplications per output pixel — every output channel is a weighted combination of every input channel, filtered spatially. Depthwise separable convolution splits this into two cheaper operations. First a depthwise step that filters each channel independently with a 3×3 kernel: 9C multiplications. Then a pointwise step, a 1×1 convolution that mixes channels: C² multiplications. Total cost is 9C + C², which for any reasonable channel count is dominated by C² — about a factor of nine cheaper than the standard convolution it replaced.

You lose a little expressiveness. Channels can no longer mix during the spatial filter; they only mix afterwards. For most vision tasks the loss is small, and MobileNetV2 patches it further with inverted residual blocks and linear bottlenecks. MobileNetV3 ran neural architecture search on top to tune layer widths and activation choices for mobile CPUs. The whole MobileNet family is parameterized: a width multiplier (0.25, 0.35, 0.5, 0.75, 1.0) shrinks every layer's channel count, and a resolution multiplier shrinks the input. You can dial a MobileNet down to fit almost any memory or latency budget at the cost of accuracy.

EfficientNet uses a different trick. Instead of scaling depth, width, or resolution independently, it scales all three together in a fixed ratio derived from search. Adding layers without adding width creates a representational bottleneck. Adding width without depth limits expressiveness. EfficientNet finds the ratio that balances them. The Lite variant strips out Squeeze-and-Excitation blocks (expensive on CPUs) and swaps Swish for ReLU6 (a simpler activation), and is the version you use on edge processors. Even Lite0, the smallest, has 4.6 million parameters and 0.4 GFLOPS — fine for a Raspberry Pi, marginal for an MCU.

SqueezeNet attacks parameter count specifically. Its Fire modules first squeeze the channel count down with 1×1 convolutions and then expand it again with a mix of 1×1 and 3×3 filters. It hits AlexNet-level accuracy with fifty times fewer parameters. But operations are not reduced in proportion — SqueezeNet is small in flash but not especially fast. That makes it a good fit when flash is the bottleneck and a poor fit when CPU throughput is.

Tiny-YOLO and YOLO-Nano are stripped-down object detectors. Detection is inherently expensive because you have to localize and classify multiple objects per frame. Tiny-YOLOv3 cuts the layer count from fifty-plus to nine, drops the resolution from 608×608 to 416×416, and reduces anchor box count. It still wants 15 million parameters and 5.5 GFLOPS — too much for most MCUs, fast enough for 20–30 frames per second on a Raspberry Pi 4.

And then, often forgotten, the non-neural option. Decision trees and random forests. No matrix multiplications. No floating-point arithmetic if you quantize the thresholds to integers. A tree with ten levels does ten comparisons per inference. On structured data — sensor features, tabular inputs, anything where you can engineer good features by hand — a random forest will outrun any neural network of comparable accuracy. Where they fail is high-dimensional raw input. You cannot run a tree directly on pixels; the feature extraction is the hard part, and that's where you need convolutions.

The lesson generalizes. Each of these architectures earned its efficiency by substituting a cheap operation for an expensive one, or by exploiting structure in a way the generic dense network did not. There is no such thing as "small without trade-off." There is only "small in the dimensions that mattered for the design."

## The Pareto frontier and how to read it

For a fixed task, models trace out a curve in accuracy-versus-cost space. Some models are dominated — there's another model that's both more accurate *and* faster, or smaller, or lower-power. Those models are not contenders. The remaining models, where you cannot improve one axis without sacrificing another, form the Pareto frontier. Selection is the act of picking a point on that frontier.

Suppose you profile six face-detection models on your custom dataset and your target hardware. TinyFace runs in 45 ms at 84% accuracy with 120 KB. MobileNetV2-0.25 runs in 80 ms at 88% with 250 KB. MobileNetV3-Small runs in 95 ms at 90% with 380 KB. MobileNetV2-0.35 runs in 110 ms at 91% with 420 KB. EfficientNet-Lite0 runs in 180 ms at 94% with 1.8 MB. ResNet18 runs in 450 ms at 96% with 11 MB.

Plot accuracy against latency and the Pareto frontier emerges. MobileNetV2-0.25 is dominated — MobileNetV3-Small is faster *or* more accurate at almost the same cost. ResNet18 is dominated by EfficientNet-Lite0, which gets to 94% accuracy in less than half the latency. The frontier is TinyFace, MobileNetV3-Small, MobileNetV2-0.35, EfficientNet-Lite0. Which point you choose depends on which constraint is binding. If you must fit in 50 ms, only TinyFace works. If you need 90% accuracy in 100 ms, MobileNetV3-Small. If you need 94% accuracy and you have 200 ms, EfficientNet-Lite0.

The frontier doesn't tell you which model to pick. It tells you which choices are even available, and which models you can stop considering.

Neural Architecture Search is the automated version of frontier exploration — specify a search space, an objective (maximize accuracy subject to latency on the target), and a search algorithm, and the machine produces an architecture optimized to your constraints. MobileNetV3 came out of NAS. So did EfficientNet's compound-scaling rule. ProxylessNAS ran the search directly on phones. Once-for-All trains a single super-network you can slice into sub-networks of different sizes without retraining.

NAS is worth the GPU-weeks when you ship millions of units and a 10% latency reduction pays for the search. For a one-off deployment, a scaled MobileNet that meets your constraints is almost always the right answer.

## Choosing a fall detector

A wearable fall detector. Three-axis accelerometer at 100 Hz. A fall must be flagged within 500 ms of impact. The device runs on a 220 mAh coin cell that has to last six months — about 2 mA average draw. Hardware is an nRF52840: Cortex-M4 at 64 MHz, 256 KB SRAM, 1 MB flash. Acceptance test demands ≥95% true-positive rate and ≤1% false-positive rate. Five candidates, all profiled on the same dataset on the same hardware.

Model A is the classical baseline: a hand-tuned threshold detector on peak acceleration and impact duration. Sub-millisecond, 1 KB of code, negligible power. 78% true positives, 8% false positives. Eight false alarms per hundred normal movements is a wearable nobody will keep on their wrist. Fails on accuracy.

Model B is a random forest of fifty trees on fifteen engineered features per one-second window — mean, variance, peak, zero-crossing rate, FFT dominant frequency. 3.5 ms latency. 200 KB of memory, which leaves only 56 KB of SRAM for everything else the firmware has to do. 92% true positives, 2% false positives. Below the 95% threshold. Fails on accuracy.

Model C is a small 1D CNN — four convolutional layers, two fully connected, 45,000 int8 parameters, 100 samples × 3 axes input. 25 ms latency on the M4 with CMSIS-NN. 45 KB of weights plus 30 KB of activations, 75 KB total. At 15 mA active for 25 ms, one inference burns 0.38 mJ. Run it once a second and the average current is 0.12 mA — sixteen times under budget. 96% true positives, 0.8% false positives. Meets every constraint with margin.

Model D is a larger 1D CNN: six convolutional layers, three fully connected, 180,000 parameters. 85 ms latency. 180 KB of weights plus 80 KB of activations equals 260 KB — four kilobytes over the SRAM limit. 98% true positives. The accuracy is beautiful and the model does not run. Fails on memory.

Model E is a two-layer LSTM, 32 units per layer, 60,000 parameters. 120 ms latency, 150 KB of memory, 1.8 mJ per inference. 97.5% true positives, 0.5% false positives. Meets every constraint. But it's five times slower than Model C and consumes nearly five times the energy for half a percentage point of accuracy.

Model C wins. Twenty-nine percent of SRAM, leaving the rest for firmware. Latency twenty times under budget. Power well inside the coin-cell budget. Accuracy past the threshold. Model E is viable but pays for accuracy that the acceptance test does not require, in latency and energy that the application does need to keep margin in.

The selection only works because every candidate was profiled on the actual hardware with the actual dataset. Model D looked best on paper. Model A worked on previous-generation devices when the accuracy bar was lower. Neither survived contact with the constraints.

What would change my mind: if a single profiling run on target hardware produced a result inconsistent with a model's measured accuracy and latency on the bench — that would tell me the deployment-aware metric I trusted (latency, memory, accuracy under quantization) was being measured wrong, and the whole frontier I plotted was off.

Still puzzling: how to compare two candidates that lie on the Pareto frontier of accuracy versus latency but differ in robustness to distribution shift — the dataset I profiled on is rarely the deployment distribution, and "margin against constraint" is not the same as "margin against drift."

---

## LLM Exercise — Chapter 11: Selecting Models for Constrained Deployment

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** A multi-model Pareto comparison module — given N candidate models, score each against the application's constraints and identify which lie on the Pareto frontier.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/compare.py to the tinyml-feasibility toolkit.

Frozen ModelCandidate dataclass:
- model: ModelSummary
- accuracy_pct: float (validation accuracy on the app's dataset; supplied by user)
- memory_verdict: MemoryVerdict
- compute_verdict: ComputeVerdict
- power_verdict: PowerVerdict
- meets_all_constraints: bool

Frozen ParetoFrontier dataclass:
- candidates: list[ModelCandidate]
- pareto_optimal_indices: list[int] (indices of candidates on the frontier)
- recommended_index: int (best feasible candidate per the chosen criterion)
- selection_criterion: Literal["max_accuracy_within_constraints", "max_margin_above_threshold", "min_latency"]
- rejection_log: dict (rejected_model_name → reason string)
- to_markdown() emits a Model Selection section matching Chapter 14's shape, including a Pareto frontier description

Public functions:
- `compare_models(candidates: list[tuple[ModelSummary, float]], target: Target, app: Application) -> ParetoFrontier`
- `pareto_frontier(candidates: list[ModelCandidate]) -> list[int]` — indices of non-dominated candidates on (latency, accuracy)

Implementation:
- For each candidate, run memory + compute + power assessments on the target.
- meets_all_constraints = all three FIT or TIGHT (not FAILS).
- Pareto frontier: candidate i is dominated if some candidate j has both lower latency AND higher accuracy. Keep non-dominated.
- selection_criterion default: "max_accuracy_within_constraints" — pick candidate on the frontier with highest accuracy_pct that meets_all_constraints. If none qualify, return None and populate rejection_log.

CLI:
- `tinyml-feasibility compare-models --app <yaml> --target <name> --models <path1>:<acc1>,<path2>:<acc2>,...` prints the ParetoFrontier including a sortable table

Tests:
- test_pareto_dominance_basic — 5 candidates with known dominance pattern, frontier returns the expected 3
- test_recommended_meets_constraints — recommended candidate's meets_all_constraints is True
- test_rejection_log_explains_failures — for a candidate that fails on memory, rejection_log[name] contains "memory"
```

---

**What this produces:** Replicates chapter 11's fall-detector worked example as a single CLI invocation. Pass 5 candidate models and the toolkit returns the Pareto frontier, the recommended candidate, and the rejection rationale for each that didn't make it.

**How to adapt this prompt:**
- *For your own project:* You provide the accuracy numbers (the toolkit can't measure them — that's your training pipeline's job). The toolkit profiles the rest.
- *For ChatGPT / Gemini:* Works as-is.
- *For Claude Code:* Best fit. Multi-model comparison generates a lot of output; pipe to a CSV or Markdown table.
- *For a Claude Project:* Add the Pareto-frontier algorithm as a reusable utility — chapter 12's optimization planner reuses it.

**Connection to previous chapters:** Aggregates the verdict outputs from chapters 5, 6, 7. Becomes the input that chapter 12's optimization planner uses to identify which candidate is closest to fitting and what compression sequence would close the gap.

**Preview of next chapter:** Chapter 12 adds `optimize.py` — given a model that almost fits, predict the savings from quantization, pruning, and distillation, in the order chapter 12 recommends.

---

## A note about AI

Model selection on embedded hardware is the trade-off chapter where every design choice closes other doors. The model will describe each choice as if the doors are still open.

Where the model genuinely helps: producing a structured comparison of candidate models against your stated constraints. The comparison is useful for surfacing the trade-offs you might otherwise miss.

Where the model does damage: ranking the candidates as if accuracy were the only constraint that mattered. In embedded contexts, accuracy is rarely the binding constraint.

The rule: you set the constraints; the model lays out the trade-offs against those constraints.

---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Vilfredo Pareto** was an Italian economist studying income distribution in 1906 when he formalized the idea that some allocations are dominated and some are not — the same Pareto frontier you used to choose between MobileNet variants.

**Run this:**

```
Who was Vilfredo Pareto, and how does his work on Pareto efficiency in economics connect to selecting embedded ML models on an accuracy-latency frontier? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"Vilfredo Pareto"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain Pareto efficiency in plain language, with one non-economics example
- Ask it to compare Pareto's original economics frontier to a modern accuracy-vs-latency frontier for embedded models
- Add a constraint: "Answer as if you're writing a sidebar in an econ-meets-engineering textbook"

What changes? What gets better? What gets worse?
