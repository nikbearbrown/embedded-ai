# Chapter 12 — Optimizing Models: Quantization, Pruning, and Distillation

You picked MobileNetV2-0.5. It came out of selection as the best candidate — 91.5% accuracy on your defect-detection validation set, the right architecture for the job, the right scaling for the target. You compile it for your STM32H7 and it almost fits. Almost. The firmware uses 600 KB of flash, the int8 weights need 1.5 MB, and the chip has 2 MB. You are 100 KB over. Latency comes in at 320 ms; the budget is 250 ms. You are 70 ms over. SRAM is fine. Accuracy after post-training quantization is 89.2%, which is above the 88% acceptance threshold.

You have three choices. Pick a different model — but selection already told you this was the best candidate. Buy a bigger chip — but the BOM is fixed and the production line is tooled. Or compress the model you have until it fits, without dropping below 88%.

Compression is the move you make when selection is right and the device is real. The three knobs are *quantization*, which lowers numeric precision; *pruning*, which removes parameters; and *knowledge distillation*, which trains a small model to imitate a larger one. Each one trades accuracy for size or speed in a different way, and they compose in a particular order if you want them to compose well.

## Quantization, and what the rounding does to you

Quantization replaces high-precision floating-point numbers with low-precision integers. A float32 weight occupies four bytes; an int8 weight occupies one. Quantizing a million-parameter model from float32 to int8 turns 4 MB of weights into 1 MB — a 75% reduction. On any processor with SIMD extensions, int8 multiplications run four to eight times faster than their float32 equivalents because the SIMD register packs more values per instruction.

The price you pay is rounding error.

The mapping is linear. You pick a `scale` and a `zero_point` so that

```
quantized = round((float - zero_point) / scale)
```

and the inverse approximates the original. If your weights span -1.5 to 1.5, the scale becomes 3.0 / 255 ≈ 0.0118 and the zero_point sits at -128. A float weight of 0.5 quantizes to 42 and dequantizes to 0.495 — error of 0.005, completely harmless.

Now suppose one of your activations spans 0.001 to 0.01. The scale becomes 0.01 / 255 ≈ 0.000039, and a value of 0.001 sits at integer 25 — but every value within ±0.00002 of 0.001 maps to the same integer. The signal there is being mashed by the rounding. This is where quantization damages accuracy: not where the dynamic range is wide, but where the dynamic range is wide *and the small-magnitude part of the range carries information*.

Two design decisions follow. The first is whether to use one scale per tensor or one per channel. Per-tensor quantization picks a single scale for an entire weight matrix; it is cheap but suboptimal when channels carry different magnitudes — some channels with weights in [-0.1, 0.1] sharing a scale with channels in [-2, 2] will see the small ones round to zero. Per-channel quantization gives each output channel its own scale and zero_point. It costs you N extra scalars per layer in flash, and almost always earns those back in accuracy. For embedded deployment, per-channel is the default.

The second decision is symmetric versus asymmetric. Symmetric quantization fixes zero_point at 0 and assumes the float range is balanced around zero — which is fine for weights and disastrous for ReLU activations, which are non-negative and waste half the int8 range under symmetric quantization. Asymmetric uses a non-zero offset and tracks arbitrary [min, max] ranges. Most modern toolchains pick symmetric for weights and asymmetric for activations; some accelerators force the choice for you.

Then there is the question of when to do the rounding. Two paths.

Post-training quantization takes a trained float32 model and converts it without retraining. You feed a calibration dataset of 100–1000 representative inputs through the network, record the range of weights and activations layer by layer, compute a scale per tensor, and rewrite the weights as int8. The whole process takes minutes. PTQ is the right tool when you don't have access to the training pipeline, when the model came from a third party, or when you need to ship by Friday. The damage to accuracy is usually 3–10%, depending on outliers, calibration set quality, and how many layers carry near-zero weights that the rounding kills.

Quantization-aware training simulates rounding during training. The forward pass quantizes weights and activations to int8 and immediately dequantizes them back to float32 for the gradient. The optimizer can see the rounding noise and finds weights that survive it. After training, you strip the fake-quantization nodes and store true int8 values. QAT typically lands at 1–3% accuracy loss instead of 3–10%, but it costs you hours or days of training time and access to the original dataset.

The rule is straightforward. Use PTQ unless it costs you more than the application can pay; then upgrade to QAT.

## Pruning, and the trap of unstructured pruning on real hardware

Pruning removes weights. The naive version sets individual weights to zero based on magnitude — drop everything below 0.01 — and the resulting matrix becomes sparse, with non-zero entries scattered everywhere. This is *unstructured pruning*. It is the version most papers measure, because you can prune 80% of weights from many networks and lose less than two percentage points of accuracy. It is also the version that does almost nothing useful on an embedded target.

Embedded inference frameworks — TensorFlow Lite Micro, CMSIS-NN, the firmware running on your MCU — assume dense matrices. Their kernels are tuned for dense GEMM. A sparse matrix multiplication needs a different data structure (compressed sparse row, coordinate format) and a different kernel. Almost no embedded platform ships those. So an unstructured-pruned model has fewer parameters, takes less flash to store the non-zero values plus their indices, and runs at exactly the same speed as the dense original. You saved storage and bought no latency or SRAM relief.

*Structured* pruning is the version that helps. Instead of zeroing individual weights, you remove entire structures: whole output channels in a convolutional layer, whole filters, whole layers. The matrix that remains is smaller but still dense. Every kernel works unchanged. Every metric improves: flash drops because there are fewer weights to store; SRAM drops because activation tensors carry fewer channels; latency drops because there are fewer multiply-accumulates per inference.

The procedure is iterative. Train the model, score each channel by its L1 norm or by the accuracy hit when you ablate it, drop the bottom 20%, fine-tune to recover, score again. Both major frameworks ship this — TensorFlow Model Optimization Toolkit's `prune_low_magnitude`, PyTorch's structured-pruning utilities and the third-party libraries that wrap them.

Accuracy versus pruning rate is non-linear. The first 20% of channels you remove cost less than 1% accuracy on most over-parameterized networks. The next 20% costs 2–4%. Sixty percent costs 5–10%. Beyond 70% the cliff arrives — accuracy collapses unless the network was wildly over-built to begin with. The sweet spot for embedded compression is 20–40%. If you need more, you stop pruning the architecture you have and switch to distillation.

## Distillation, and why soft labels are richer than hard ones

Knowledge distillation trains a small *student* model to imitate a large *teacher* model. The student learns from both the ground-truth labels and the teacher's predictions. The teacher's predictions, it turns out, contain more signal than the labels.

Imagine a ten-class classifier on an image of a cat. The hard label is a one-hot vector — cat is 1, everything else is 0. A trained teacher network looking at the same image outputs something like [0.01, 0.02, 0.85, 0.05, 0.01, 0.02, 0.01, 0.01, 0.01, 0.01]. The teacher is 85% confident it's a cat, 5% confident it's a dog, almost nothing on the other classes. That distribution carries information the hard label throws away: it tells the student which classes are visually similar, where the decision boundaries are blurry, and which mistakes are reasonable mistakes.

You train the student with a mixed loss:

```
L_student = α · L_hard + (1 - α) · L_soft
```

`L_hard` is the cross-entropy against the ground-truth label. `L_soft` is the cross-entropy against the teacher's distribution, both softened by a temperature `T` greater than 1. Higher temperature flattens the distribution and emphasizes the relative probabilities of the wrong classes — that's the part of the teacher's knowledge you most want to transfer. A student trained this way typically gains 2–5% accuracy over the same student trained from scratch on hard labels alone.

Distillation is the right move when you have a much larger teacher available, when the student's architecture cannot reach the teacher's accuracy by training directly, and when you have access to the training data. It pairs naturally with pruning: prune the architecture down, then distill the pruned student against the original teacher to claw back the accuracy that the pruning gave up.

## Order matters

The three techniques compose, but only in one order without surprises. Prune first. Distill second. Quantize last.

Prune first because you want the smaller, simpler model to be the thing the rest of the pipeline operates on. Quantizing a network and then removing channels from the quantized version is poorly supported by frameworks; pruning a float32 network is the well-trodden path.

Distill second because the pruned student is the architecture you actually want to deploy, and distillation is the most efficient way to recover accuracy that pruning gave up. The teacher you distill against is the original large float32 model.

Quantize last because the deployed weights need to be int8, and the calibration step in PTQ — or the fake-quantization nodes in QAT — should see the final architecture, not an intermediate one.

What you do not do is prune aggressively (60% or more) and then quantize. Both steps add error; they compound; the result is sometimes catastrophic. If the application demands more than 60% compression, the right move is not extreme pruning of an existing architecture. The right move is distillation onto a smaller architecture that was designed to be small.

## The MobileNetV2-0.5 that almost fit

Back to the chapter's puzzle. MobileNetV2-0.5 on an STM32H7. Firmware uses 600 KB. Int8 weights are 1.5 MB. Total flash demand 2.1 MB on a 2 MB part — over by 100 KB. SRAM is 280 KB of activations on a chip with 1 MB, so SRAM is fine. Latency 320 ms against a 250 ms budget. Accuracy 89.2% int8 against an 88% threshold.

Apply 25% structured pruning. Channels go away across all the layers. After fine-tuning the pruned network recovers most of the lost accuracy:

- Parameters drop from 1.5 M to 1.125 M.
- Int8 flash drops from 1.5 MB to 1.125 MB. Total flash with firmware: 1.725 MB. Fits in 2 MB with 275 KB of margin.
- SRAM activations drop proportionally to 210 KB. Fine.
- Latency drops 25% to 240 ms. Inside the 250 ms budget by 10 ms.
- Accuracy lands at 89.8% on the pruned-and-fine-tuned model.

Pruning alone solved the problem. Flash is comfortable; latency is back inside the budget; accuracy is still above threshold. But you have only 10 ms of latency margin, which is uncomfortable — the next firmware update that adds a feature could easily push you over. Two options: leave it alone and accept that next year's update is going to be a fight, or apply distillation now and buy back accuracy headroom that lets you tolerate a little latency creep.

If you distill the pruned-architecture student against the original float32 MobileNetV2-0.5 as teacher, the student picks up about 0.8% accuracy: 90.6% instead of 89.8%. Latency, memory, and flash do not change — distillation does not alter the architecture. What it gives you is buffer against the threshold, so future quantization-aware re-tuning or further pruning has somewhere to take from.

The model that ships: 1.125 M int8 parameters, 1.725 MB total flash, 290 KB total SRAM, 240 ms latency, 90.6% accuracy. Pruning earned the fit. Distillation earned the margin. Quantization, applied earlier in the pipeline, was the thing that made any of the rest possible by cutting weight memory by 75%.

## What compression cannot fix

Optimization is the final move, not the rescue mission. There are problems compression does not solve.

If your model is below the accuracy threshold before optimization, compression makes it worse. You need a better base model, more training data, or a different architecture — not smaller weights.

If your architecture is fundamentally wrong for the task, compression does not change that. A pruned and distilled ResNet is still a ResNet, and a ResNet on raw audio will lose to a properly designed 1D CNN no matter how aggressively you compress it.

If your latency is ten times over budget, compression cannot save you. Pruning and quantization together typically buy you a factor of two to four. A factor of ten requires faster hardware, or a different model class, or both.

If the model uses operations the target hardware doesn't accelerate — attention layers on a chip without matrix-multiply units, dynamic control flow on a static-graph runtime — compression cannot remove the architectural dependency. You change the model or you change the hardware.

The compression knobs are powerful inside their range and useless outside it. Selection is what gets you into the range. Optimization is what gets you the rest of the way.

What would change my mind: if a calibrated experiment showed structured pruning + QAT producing systematically *worse* accuracy on a given architecture-and-dataset combination than QAT alone — that would tell me the prune-first ordering rule isn't a property of the techniques but a property of *how I'm fine-tuning between them*, and the right rule depends on the fine-tuning protocol.

Still puzzling: why per-channel quantization helps so much on some architectures and barely at all on others. The naive story is "channel imbalance," but I've seen networks with very imbalanced channel magnitudes survive per-tensor quantization unharmed and others with seemingly balanced channels collapse without per-channel scales. There is something about how the imbalance interacts with downstream layers that I do not fully see.

---

## 🛠️ LLM Exercise — Chapter 12: Optimizing Models — Quantization, Pruning, Distillation

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** An optimization-plan recommender that takes a model that almost fits and predicts the size, latency, and accuracy after each compression step in the prune → distill → quantize order.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/optimize.py to the tinyml-feasibility toolkit.

Frozen OptimizationStep dataclass:
- technique: Literal["prune", "distill", "quantize_ptq", "quantize_qat"]
- predicted_param_count: int
- predicted_largest_activation: int
- predicted_latency_ms: float
- predicted_accuracy_pct: float
- predicted_accuracy_drop_pct: float
- justification: str  (why this step was inserted at this position)

Frozen OptimizationPlan dataclass:
- baseline_model: ModelSummary
- baseline_accuracy_pct: float
- target_constraints: dict  (the four-constraint targets)
- accuracy_floor_pct: float
- steps: list[OptimizationStep]
- final_predicted_metrics: dict
- meets_all_constraints_after_plan: bool
- meets_accuracy_floor_after_plan: bool
- to_markdown() emits an Optimization Plan section matching Chapter 14's shape

Public functions:
- `recommend_optimization_plan(model: ModelSummary, target: Target, app: Application, baseline_accuracy: float) -> OptimizationPlan`
- `predict_pruning(model, prune_pct: float) -> dict` — pruning by N% reduces param_count by N%, largest_activation by N% (proportional), accuracy drop ~1% per 20% pruned (non-linear, document the heuristic)
- `predict_distillation(model, teacher_model) -> dict` — typical recovery 2-5% accuracy
- `predict_quantization(model, mode: Literal["ptq", "qat"]) -> dict` — int8 PTQ: param size × 0.25, accuracy drop 3-10%; QAT accuracy drop 1-3%

Implementation:
- Run baseline assessments. If FITS, OptimizationPlan.steps = [] (no compression needed).
- If FAILS or TIGHT, follow the prune → distill → quantize order from chapter 12.
- Conservative defaults: prune 25%, distill if accuracy drops below floor after pruning, quantize last (PTQ default; recommend QAT if accuracy floor is tight).
- After each step, predict whether the constraints close. Stop adding steps when they do, or flag "INSUFFICIENT" if the chain bottoms out without closing.

CLI:
- `tinyml-feasibility plan-optimization --app <yaml> --target <name> --model <path> --baseline-accuracy <pct>` prints the OptimizationPlan with predicted accuracy after each step

Tests:
- test_no_optimization_when_fits — small model + big target, plan.steps is empty
- test_quantize_only_for_flash_overrun — model 30% over flash, plan = [quantize_ptq], final fits
- test_full_chain_for_aggressive_compression — model 3× over budget, plan = [prune, distill, quantize_qat], document each step's justification
- test_insufficient_compression_flagged — model 10× over budget, expect INSUFFICIENT with rationale
```

---

**What this produces:** Given the chapter 12 puzzle (MobileNetV2-0.5 100 KB over flash and 70 ms over latency), the toolkit emits the same plan the chapter narrates: "prune 25% of channels — fits with 10 ms margin; distill against teacher — recover 0.8% accuracy; PTQ already applied."

**How to adapt this prompt:**
- *For your own project:* The baseline_accuracy you pass in is the float32 accuracy you measured during training. The toolkit predicts the deployed accuracy.
- *For ChatGPT / Gemini:* Works as-is.
- *For Claude Code:* Best fit.
- *For a Claude Project:* Pin the prune→distill→quantize ordering rule and the per-technique heuristics to the system prompt.

**Connection to previous chapters:** Reads ModelSummary (3) and the verdict modules (5, 6, 7). Outputs feed chapter 13's deployment plan and chapter 14's report.

**Preview of next chapter:** Chapter 13 adds `deploy.py` — a TFLite converter wrapper that runs the conversion and verifies on-device output against Python output, catching the silent-failure mode the chapter opens with.

---

## 🕰️ AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Jacob Ziv** co-invented the LZ77 and LZ78 algorithms — the lossless-compression theory that underlies every ZIP file. Quantizing a neural network is the lossy cousin: same idea, different trade-off.

**Run this:**

```
Who was Jacob Ziv, and how does his work on lossless compression with Abraham Lempel connect to lossy techniques like int8 quantization and pruning in embedded ML? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"Jacob Ziv"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain how LZ77 compression works in plain language, with one tiny example
- Ask it to compare lossless LZ compression to lossy int8 quantization on the same trade-off axes
- Add a constraint: "Answer as if you're writing a chapter epigraph for a model-compression textbook"

What changes? What gets better? What gets worse?
