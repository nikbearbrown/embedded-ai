# Chapter 4 — Inference Mechanics

You have a trained model. You have selected hardware. The model fits in flash, the activations fit in RAM, and the theoretical inference latency calculated from FLOP count and processor throughput is within budget. You compile, flash the firmware, run the first test — and the inference takes three times longer than predicted, or the output is NaN, or the system halts halfway through with a memory fault.

This is not a rare failure. It is the *default* outcome the first time you deploy on constrained hardware, because the theoretical analysis from the previous two chapters is necessary but not sufficient. The numbers from the spec sheet are upper bounds on what the hardware can do. Whether your specific model, compiled by your specific toolchain, on your specific configuration of cache and clock and memory layout, achieves anything like those upper bounds is an empirical question. This chapter is about how to ask and answer that question, and how to recognize what the answer is telling you when the gap between prediction and reality is large.

When you call the inference function, a sequence of stages runs in a specific order. Stage 1 is *input preparation* — sensor data arrives raw (ADC samples, pixel values, raw register reads), and you have to normalize it to whatever range the model was trained on, reshape it into the right tensor dimensions, and convert it to the right numeric type. If preprocessing includes an FFT for audio features or image rescaling, this stage can dominate. Stage 2 is *inference execution* — the computational graph runs layer by layer, each layer reading its weights from flash or a cached copy in SRAM, reading its input activations, computing convolutions or matmuls or activations, and writing output activations to the next layer's input buffer. This is where most of the time goes. Stage 3 is *output interpretation* — applying softmax, non-max suppression, threshold logic, anything that turns the model's raw output into something actionable. Stage 4 is *result delivery* — setting a GPIO, writing a flash log, sending a LoRaWAN packet. When you measure *inference latency* from a profiler, you are usually measuring Stage 2 only. When the application has a hard deadline, what matters is Stages 1 through 4 end to end. A 50 ms inference can become a 150 ms application latency if you forgot to count the FFT and the network transmission.

On a bare-metal system — your firmware running directly on the processor with no operating system — the pipeline is deterministic. You allocate memory once at startup, the processor runs at a fixed clock with no other tasks competing for it, and inference takes the same time on every pass barring cache effects or thermal events. On an RTOS like FreeRTOS or Zephyr, inference runs as a task and can be preempted. The 200 ms inference might spread across 250 ms of wall-clock time when a higher-priority task interrupts. Most embedded AI deployments end up using bare-metal for latency-critical paths and an RTOS for systems where AI is one of several concurrent functions, with the inference task running at a priority chosen to match the real-time requirement.

The reason theoretical FLOP-based latency predictions fail is that operations are not all compute-bound the way the FLOP count assumes. Some are *memory-bound* — their execution time is set by how fast data moves between memory and the processor, not by how fast the processor multiplies. Take a matrix multiplication, *C = A × B*, with *A* of shape *M × K* and *B* of shape *K × N*. The MAC count is *M × N × K*. On a Cortex-M4 with FPU at 100 MHz, each MAC takes one cycle when operands sit in registers. If A is 128 × 128 = 16,384 elements as float32, you cannot keep it all in registers — it has to come out of SRAM, and each SRAM read costs cycles. For the 128 × 128 by 128 × 10 multiply that is 163,840 MACs of compute, plus 16,384 SRAM reads at maybe 2 cycles each, which adds 32,768 cycles of *just memory traffic*. The operation that should take 1.6 ms takes 3–5 ms instead, because it is memory-bound, not compute-bound.

A Cortex-M7 with 16 KB of L1 data cache, running the same operation with cache-aware blocking — multiplying in 64 × 64 sub-blocks so each sub-block stays in cache while it is reused across multiple output elements — gets back to something close to the theoretical limit. Same operation count. Different memory locality. Order-of-magnitude difference in actual time.

Convolution is even more memory-intensive than matmul. A 2D convolution with a 3 × 3 kernel requires loading 9 input pixels for every output pixel; for a 96 × 96 input with 32 channels convolved into 32 output channels, that's 96 × 96 × 32 × 9 × 32 ≈ 84 million memory accesses. If those activations are in external PSRAM rather than on-chip SRAM, each access costs roughly 10–20 cycles instead of 1–2, and inference latency can grow by an order of magnitude. The compute did not change. The memory pattern did, and the memory pattern is what dominated.

Activation functions are the cheap end of compute, but they can be memory-bound too if you do not fuse them with the layer that produced the input. ReLU is conceptually one comparison and a conditional write per element; on a pipelined processor the conditional branch can mispredict and flush the pipeline. SIMD-vectorized implementations process 4 or 8 elements per instruction without branches, eliminating the issue. CMSIS-NN's optimized kernels do this; the reference C implementation in TFLite Micro does not, and that gap alone can be a 3–5× latency difference.

Hardware accelerators — neural processing units, vector engines — change the execution model again. An NPU includes dedicated matrix-multiply hardware that does hundreds of MACs per cycle. An operation that takes 100,000 CPU cycles can take 1,000 NPU cycles, *but only if it maps to the accelerator's supported primitives*. Standard 3 × 3 convolutions usually map well. Depthwise convolutions might map poorly if the accelerator does not natively support channel-wise operations. Attention mechanisms or dynamic control flow rarely map at all and fall back to the CPU.

Memory allocation strategy is the second big determinant of whether deployment works. *Dynamic* allocation during inference — `malloc()` calls inside the inference path — is a failure mode on embedded systems, not a feature. The heap is a fixed region of SRAM. Allocations come out of it, and freed memory returns to it, but fragmentation can leave you unable to satisfy a future allocation even when total free memory is sufficient. There is no swap. There is no other process to terminate. Failed allocation either crashes or returns null. And `malloc()` itself is not free — it can spend hundreds of microseconds searching the heap, which becomes milliseconds if you call it inside a per-layer loop.

The right pattern for embedded inference is *static pre-allocation*. All inference memory is allocated once during initialization, before the first inference runs. That includes the model weights (loaded from flash into SRAM if needed, or accessed directly from flash), the activation buffers for every layer's intermediate results, scratch buffers for things like im2col transformations, and the input and output tensors. The total goes into one contiguous block of SRAM — TensorFlow Lite Micro calls it a *tensor arena* — and the inference engine manages it internally. With buffer reuse, peak memory is the size of the largest layer's output plus whatever buffers have to coexist. Without buffer reuse, peak is the sum of all of them, which is wasteful by an order of magnitude for moderately deep networks. Static allocation also lets you fail at *compile time* rather than at runtime: if your activation memory needs 250 KB and your part has 200 KB of SRAM, the build tells you immediately, and you do not waste time debugging mysterious runtime crashes that turn out to be heap exhaustion.

If you see `malloc()` calls in your inference code path, something is misconfigured. Trace them, find the source, replace them with pre-allocated buffers. *Embedded inference allocates zero memory during the inference itself.*

Now you have to measure. The most basic profiling on ARM Cortex-M cores uses the Data Watchpoint and Trace unit's cycle counter. You enable it once during initialization, read it before inference starts, read it after inference completes, subtract:

```c
// Enable DWT cycle counter (once during init)
CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
DWT->CYCCNT = 0;
DWT->CTRL  |= DWT_CTRL_CYCCNTENA_Msk;

// Measure inference
uint32_t start = DWT->CYCCNT;
run_inference();
uint32_t end   = DWT->CYCCNT;
uint32_t cycles = end - start;

// Convert to time
float latency_ms = (cycles / (float)CPU_FREQ_HZ) * 1000.0f;
```

At 100 MHz, 10 million cycles is 100 ms. The same pattern wrapped around individual layers gives operator-level profiling — and for most embedded ML frameworks you do not have to wrap manually. TFLite Micro has built-in profiling that reports per-operator timing over UART when you enable it at compile time. The output looks like

```
Operator,           Count, Time (ms)
CONV_2D,                1,       45.2
DEPTHWISE_CONV_2D,     13,       82.3
FULLY_CONNECTED,        1,        3.1
SOFTMAX,                1,        0.8
Total inference time:        131.4 ms
```

If 63% of inference time is depthwise convolutions, you know exactly where to spend optimization effort. Without that breakdown, you are guessing.

Profiling has to account for variance. Run inference 100 times and look at the distribution. If every run lands between 130 and 132 ms, latency is stable. If runs vary from 120 to 180 ms, there is non-determinism — cache effects, interrupt handling, thermal throttling — and for soft real-time you can use the mean or 95th percentile, but for hard real-time you have to use the worst case observed plus margin.

Energy profiling needs hardware: a current-sense amplifier on the supply rail, logging current as a function of time. Integrate to get energy per inference. For a 3.3 V part drawing 40 mA during 150 ms of inference, energy is 3.3 × 0.040 × 0.150 = 19.8 mJ per inference. If inference runs every 10 seconds, average power is 1.98 mW. A 1,000 mAh cell at 3.3 V stores about 11,880 J, and 11,880 / 0.00198 ≈ 6 million seconds, or about 69 days of battery life. The same arithmetic from Chapter 2; the only difference is that you are now measuring the active current rather than reading it from the spec sheet.

Numerical precision is the third axis. Networks are trained in float32 and quantization is what gets you down to float16, bfloat16, or int8. float32 is the baseline — about seven decimal digits, four bytes per value, slow on processors without an FPU. float16 halves memory but is rare on microcontrollers, which usually emulate it in software and run *slower* than they would on float32 with the FPU. The big win on most embedded targets is int8, which halves memory again to one byte per value, plus enables SIMD that processes four int8 values per 32-bit register per instruction — a 4× throughput gain on Cortex-M4 and higher on dedicated accelerators. ARM's Ethos-U55, for instance, gets roughly 64× the int8 MAC throughput of float32 on the same chip.

The cost of int8 is precision. Quantization shifts and scales the float32 ranges of weights and activations onto the [-128, 127] integer range, and the rounding errors accumulate through the network. *Post-training quantization* (PTQ) takes a trained float32 model, measures the dynamic ranges over a calibration dataset, computes scaling factors, and converts. Cheap, easy, and for image classification it usually costs 1–3% accuracy. *Quantization-aware training* (QAT) simulates quantization during training so the model learns weights that survive it, and gets you better accuracy at the cost of having to retrain. For some models — those with batch normalization or extreme activation ranges — naive PTQ can destroy accuracy entirely, and you either tune ranges per layer or fall back to mixed precision (most layers int8, the sensitive ones float32).

The pattern you should commit to: deploy float32 first, measure latency and memory, quantize to int8 if the budget demands it, *measure accuracy before and after*, and never assume the conversion is free.

To make all of this concrete, work an actual deployment. You have a keyword-spotting model — depthwise separable CNN, 80,000 parameters, ~22 million MACs per inference. Theoretical analysis: 320 KB weights as float32, 45 KB activation memory, latency 22M / 60 MMAC/s ≈ 367 ms on a 64 MHz Cortex-M4 with FPU like the Arduino Nano 33 BLE Sense (nRF52840, 256 KB SRAM, 1 MB flash).

You compile with TFLite Micro, flash, run. First inference: **1,200 ms.** Three times slower than the prediction.

Diagnose. Check precision first — the model is float32, the FPU is there, that should be efficient. But the build is using the *reference* C kernels, not the optimized CMSIS-NN ones. The reference implementation does not use the FPU effectively or the DSP/SIMD extensions, and runs 3–5× slower. Reconfigure the build to use CMSIS-NN, recompile, re-flash. **420 ms** — close to the 367 ms prediction, but still over budget if the application wants 100 ms.

Now identify the bottleneck. Enable per-operator profiling. Two depthwise convolutions consume 71% of the total — 180 ms and 120 ms respectively, on 32 × 32 and 24 × 24 feature maps with 64 channels each. Why are they so slow? Check the memory layout. The activations exceed the on-chip SRAM budget once everything else is accounted for, and have spilled into external memory. External access costs about 10× more than on-chip SRAM access; the depthwise convolutions are memory-bound on the external path. Fix: shrink the model so all activations fit in on-chip SRAM. Retrain with smaller maximum feature maps (16 × 16 instead of 32 × 32). Activation memory drops to 28 KB. **140 ms.**

Still over the 100 ms target. Quantize. Post-training int8 quantization. Model size drops to 80 KB, activation memory stays at 28 KB, and SIMD does its 4× thing. **45 ms.** Accuracy goes from 94.2% before quantization to 92.8% after — a 1.4% loss, well within tolerance for the application. Memory: 80 KB flash, 28 KB RAM. Latency: 45 ms. Power: separate measurement.

Theoretical analysis predicted 367 ms. Deployment measured 1,200 ms. Profiling identified the bottleneck twice — first kernels, then memory layout. Optimization brought it to 45 ms. The theoretical prediction was directionally correct and quantitatively wrong by 25×, and only target-hardware profiling revealed why. *That gap is not unusual. It is the work this chapter was written about.*

When inference fails on a real target, the four categories of failure are crashes, wrong output, slow latency, and excessive power. *Crashes* — a HardFault or memory exception during inference — usually mean a buffer overrun. The tensor arena is too small and the engine is writing past the end, or the stack is overflowing because the call chain is deeper than allocated. Increase the arena, increase the stack, retest. *Wrong output* — NaN, Inf, predictions that miss accuracy by a wide margin — usually means precision or preprocessing. Check that the quantization scale and zero-point parameters match between training and inference. Check that the input is normalized to the range the model expects (a model trained on inputs in [0, 1] will produce nonsense if you feed it raw 12-bit ADC values from 0 to 4095). Check tensor layout — NHWC versus NCHW — matches what the model was exported with. *Slow latency* — 10× slower than predicted — usually means non-optimized kernels, or activations spilled into external memory, or the clock running at a different speed than you think. *Excessive power* — battery draining at twice the duty-cycle math — usually means busy-waiting (the processor stays active polling instead of sleeping while inference completes), or peripherals left on (LEDs, sensors, communication modules drawing current you forgot to count), or the part not entering its lowest-power sleep mode because something is keeping it awake.

These four categories cover most deployment failures. The diagnostic discipline is the same in every case: profile latency, measure memory usage, log output values, and compare against predictions. The gap between what you predicted and what you measured is what tells you where the problem is, and the better your prediction was, the more informative the gap.

The next chapter goes deep on the first of the four constraints in detail — memory — and looks specifically at why models that fit in total memory still fail at runtime, and what to do when they do.

---

## 🛠️ LLM Exercise — Chapter 4: Inference Mechanics

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** A latency predictor that decomposes a model's inference into the four pipeline stages and estimates each stage's wall-clock time on a given target.
**Tool:** Claude Code

---

**The Prompt:**

```
Extend tinyml-feasibility with a latency-prediction module grounded in the four-stage pipeline (acquire, preprocess, run, postprocess).

Add src/tinyml_feasibility/profiling.py:

Frozen LatencyEstimate dataclass:
- acquire_ms: float  (sensor read time; default 1.0, override by app config)
- preprocess_ms: float  (e.g., MFCC for audio, normalization for vision)
- inference_ms: float
- postprocess_ms: float
- total_ms: float
- bottleneck_stage: Literal["acquire", "preprocess", "run", "postprocess"]
- assumption_notes: list[str]  (every estimate that came from a lookup table goes here)

Public functions:
- `predict_inference_ms(model: ModelSummary, target: Target) -> float` — uses MAC throughput lookup. Provide a CORE_THROUGHPUT dict mapping core string ("Cortex-M0+", "Cortex-M4", "Cortex-M7", "Cortex-M55", "Cortex-A53") to MAC/sec at 1 MHz with int8 + CMSIS-NN. Source each value with a citation comment (e.g., ARM benchmark URLs, CMSIS-NN README).
- `predict_pipeline(model, target, app) -> LatencyEstimate` — returns full breakdown.

CLI extension:
- `tinyml-feasibility predict-latency --app <yaml> --target <name> --model <path>` prints the LatencyEstimate with bottleneck_stage flagged.

Tests:
- test_predict_inference_scales_with_clock — same model on Cortex-M4 at 64 MHz vs 128 MHz: latency at 128 MHz is approximately half (within 10%)
- test_predict_inference_scales_with_macs — doubling MAC count approximately doubles inference latency
- test_pipeline_bottleneck_correctness — for a synthetic case where preprocess dominates, bottleneck_stage == "preprocess"

Note: the lookup tables are imperfect approximations. Document this clearly in the module docstring — the tool predicts within roughly 2x of measured latency on real hardware. Real profiling on target is still required before committing to a deployment.
```

---

**What this produces:** `tinyml-feasibility predict-latency --app jaguar.yaml --target STM32L4R5 --model jaguar_dscnn.tflite` returns a four-stage latency breakdown with the bottleneck stage flagged and explicit assumption notes.

**How to adapt this prompt:**
- *For your own project:* Override the default `acquire_ms` and `preprocess_ms` in your application YAML if your sensor or preprocessing pipeline is non-standard.
- *For ChatGPT / Gemini:* Works as-is. Both will fabricate throughput numbers if not pinned to citations — be aggressive in the prompt about NO FABRICATION and require URLs in comments.
- *For Claude Code:* Use `--allowed-tools edit,bash,web_search`; it will look up CMSIS-NN benchmarks for the throughput table.
- *For a Claude Project:* Add the CORE_THROUGHPUT dict to a shared file in the project so chapters 6 and 8 can extend it.

**Connection to previous chapters:** Consumes the ModelSummary (chapter 3) and Target (chapter 2). Produces the latency input that chapter 6 will compare against the latency budget.

**Preview of next chapter:** Chapter 5 adds the first verdict module — `memory.py` — which compares a model's flash + SRAM demands against a target's budget and emits a FITS / TIGHT / FAILS verdict with named mitigations.

---

## 🕰️ AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Thelma Estrin** built one of the first real-time biomedical computing systems — getting EEG signals into a computer fast enough to be useful — when "real-time" still meant tape and paper.

**Run this:**

```
Who was Thelma Estrin, and how does her work on real-time biomedical computing at UCLA connect to today's inference pipelines on embedded processors? Three paragraphs. End with the single most surprising thing about her career.
```

→ Search **"Thelma Estrin"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain what real-time biomedical signal processing meant in the 1960s, in plain language
- Ask it to compare Estrin's EEG digitization pipeline to a modern wearable's inference pipeline
- Add a constraint: "Answer in the form of an oral-history interview transcript"

What changes? What gets better? What gets worse?
