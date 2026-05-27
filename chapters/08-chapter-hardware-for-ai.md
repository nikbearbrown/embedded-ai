# Chapter 8 — Hardware for AI

Your model runs correctly on a Cortex-M4 at 100 MHz, but inference takes 850 ms and your deadline is 100 ms. You have already quantized to int8, pruned 30% of the weights, and reordered layers for cache locality. The model cannot get smaller without accuracy falling below the application's floor. The CPU cannot get faster without changing the chip. You evaluate an STM32N6 with a built-in NPU. The same model now runs in 45 ms. The latency constraint is satisfied, and power drops 60% because the accelerator finishes inference in a fifth of the time. But the STM32N6 costs $12 per unit instead of $3, the toolchain is more complex, and the NPU only accelerates certain operations — your model's depthwise convolutions fall back to the CPU, capping the real speedup. The decision is not obvious.

That decision — when a hardware accelerator is the right answer, and when it is not — is the subject of this chapter. The short version is that accelerators solve the compute constraint at the cost of cost, complexity, and inflexibility, and the question is always whether what you give up is worth what you get.

The reason CPUs are inefficient for inference is structural. A general-purpose CPU is designed to execute arbitrary instruction sequences with maximum flexibility — complex pipelines, branch prediction, out-of-order execution, caches to handle unpredictable workloads. That flexibility costs energy and silicon area on control logic instead of arithmetic. Neural-network inference is the *opposite* of arbitrary: a regular computation, millions of multiply-accumulates with predictable data flow and almost no branching. A CPU executing inference spends most of its energy fetching instructions, managing the cache, and shepherding the pipeline, not doing arithmetic. On a Cortex-M7 at 400 MHz running a 128 × 128 matmul (about 2.1 M MACs), roughly 30% of cycles are arithmetic, 50% are memory access, 15% are instruction fetch and decode, and 5% are pipeline stalls and cache misses. *Two-thirds of the CPU's time is overhead.* A specialized accelerator removes most of that overhead.

![Two stacked horizontal bars comparing how a Cortex-M7 CPU and a 16x16 NPU MAC array spend each cycle running a 128x128 int8 matmul. The CPU bar splits 30% arithmetic, 50% memory access, 15% instruction fetch and decode, 5% pipeline stalls; an overhead bracket spans the right 70%. The NPU bar is roughly 92% arithmetic with a thin sliver of data movement.](../images/chapter-08-hardware-for-ai-fig-01.png)
*Figure 8.1 — Where each cycle goes on a 128×128 matmul. A CPU spends two-thirds of its cycles on overhead. An NPU's silicon is the arithmetic.*

An NPU designed for matmul has dedicated MAC units arranged in a 2D array (commonly 8 × 8, 16 × 16, or 32 × 32 MACs in parallel), local scratchpad memory close to the compute (no cache, no arbitrary access patterns), and a simple controller that sequences operations without per-cycle instruction fetch. The same 128 × 128 matmul on a 16 × 16 MAC array does the arithmetic in $(128/16)^3 = 512$ cycles plus memory transfer, which at 400 MHz lands around 1.3 ms — about 8× faster than the CPU. The speedup comes from parallelism (256 MACs per cycle versus 1) and the absence of control overhead. The cost: the NPU is not a general processor, it executes only what its MAC array and memory architecture support, and any operation it cannot run falls back to the CPU. *That fallback is where most of the disappointment with NPU performance comes from.*

![Block diagram of a microNPU. External memory on the left connects through a DMA engine to a local SRAM scratchpad. The scratchpad feeds a 16x16 grid of MAC processing elements. The MAC array writes back to an accumulator and then to the scratchpad. A thin sequencer on the right issues control signals (dashed) to the DMA, scratchpad, and MAC array.](../images/chapter-08-hardware-for-ai-fig-02.png)
*Figure 8.2 — microNPU dataflow. Local scratchpad feeds a parallel MAC grid; a thin sequencer replaces the CPU's fetch/decode machine.*

Three classes of accelerator matter for embedded AI: DSPs, NPUs, and FPGAs.

DSPs are signal-processing CPUs — TI's C674x, ARM's Cortex-M55, parts purpose-built for filtering, FFT, correlation. They are not AI-specific, but they are very good at certain AI operations because they have multiple MAC units in parallel (2–8 per cycle), SIMD instructions on packed 8-bit and 16-bit values, dedicated address-generation units for stride and circular-buffer patterns, and zero-overhead loop counters. They run fully connected layers, 1D convolutions (audio, time series), depthwise separable convolutions, and fixed-point quantized models efficiently. They struggle with 2D convolution (the address patterns exceed what the AGUs handle cleanly), pooling and activations, and dynamic models. As a quick comparison: a 1D-CNN keyword spotter at 18 M MACs runs in about 300 ms on a Cortex-M4 at 100 MHz with CMSIS-NN, and about 90 ms on a TI C5535 DSP at the same clock — 3.3× faster from more MAC units and better SIMD utilization, at the cost of more power (roughly 2× active current) and a different toolchain. DSPs occupy a middle ground: better than CPUs for signal-heavy AI, worse than NPUs for general inference, but uniquely good when your application combines both AI and traditional DSP (FFT-based audio features, sensor filtering) on the same chip.

NPUs are domain-specific accelerators built only for inference. They divide into three size classes. *Datacenter NPUs* (Google TPU, NVIDIA TensorRT) have thousands of MACs and gigabytes of on-chip memory; not relevant for embedded. *Edge NPUs* (Coral Edge TPU, Hailo-8, Intel Movidius) carry 100–1,000 MACs and megabytes of memory at 0.5–5 W; designed for cameras, drones, edge gateways. *MicroNPUs* (ARM Ethos-U55, STM32 AI core, Syntiant NDP120) sit at the microcontroller scale — 8–256 MACs, kilobytes to a couple of megabytes of memory, 10–200 mW. The microNPU is the class that integrates with or pairs with an MCU.

![Log-log scatter plot of NPU MAC count against active power. Three clusters appear. Bottom-left: microNPUs including Syntiant NDP120, Ethos-U55, STM32N6, and K210 at 64 to 512 MACs and 0.2 to 300 mW. Middle: edge NPUs including Coral Edge TPU, Hailo-8, and Movidius at hundreds to thousands of MACs and 1.5 to 2.5 W. Top-right: datacenter NPUs including TPU v4 and H100 / TensorRT at over 100,000 MACs and 200 to 350 W. A box highlights the microNPU cluster as the embedded class.](../images/chapter-08-hardware-for-ai-fig-03.png)
*Figure 8.3 — NPU classes by MAC count vs power. Embedded AI lives in the bottom-left cluster; the other two are different planets.*

The ARM Ethos-U55, paired with Cortex-M55 or Cortex-M85 cores, is representative. It comes configured with 32, 64, 128, or 256 MACs (chosen at SoC design time), supports int8 and int16 quantized models, and ships with 128 KB to 2 MB of on-chip SRAM. At 500 MHz with 256 MACs, peak throughput is 128 G int8 MACs/s. For a 50 M MAC model, theoretical latency is about 390 ms — but real performance depends on whether the model's operations map onto the accelerator. The Ethos-U55 accelerates 2D convolution (standard and depthwise), fully connected layers, pooling, and element-wise operations (add, multiply, ReLU). It does not accelerate attention mechanisms, custom activation functions, sparse operations, or dynamic control flow — those fall back to the CPU. A model that is 80% accelerated operations and 20% non-accelerated operations does not get the full 10× speedup; it gets more like 3–5× because the CPU bottleneck dominates the unaccelerated portions. *The mapping of model to accelerator is the constraint, not the accelerator's peak throughput.*

![Block diagram. An operation router at the top splits incoming model ops into two streams. Solid arrows route supported ops (conv2d, depthwise, fully connected, pooling, element-wise) to an Ethos-U55 microNPU on the left. Dashed arrows route unsupported ops (attention, custom activations, sparse, dynamic control flow) to a Cortex-M55 host CPU on the right. Both blocks share an SRAM pool over an AXI bus. A callout notes that 80 percent accelerated yields only 3 to 5x realised speedup because CPU fallback dominates.](../images/chapter-08-hardware-for-ai-fig-04.png)
*Figure 8.4 — Cortex-M55 + Ethos-U55 routing. The mapping of model ops to accelerator decides realised speedup; peak throughput is the ceiling, not the floor.*

The STM32N6 takes the integrated approach further: an 800 MHz Cortex-M55 plus a proprietary NPU rated at 3 TOPS for int8, with 2.5 MB SRAM and 4 MB flash. A 40 M MAC MobileNetV2 runs in about 180 ms CPU-only on this part, and 45 ms with the NPU active — a measured 4× speedup that is real and transformative for vision applications with hard latency targets. The trade is BOM cost: $12–15 per part versus $4–6 for an STM32H7 without NPU. At 100,000 units per year, that gap is $800,000.

FPGAs are the third option, and they answer a different question. Where a CPU is flexible-but-slow and an NPU is fast-but-rigid, an FPGA is *configurable* — you design exactly the circuit you need (custom MAC array sizes, custom data paths for unusual operations, bit-level precision options, pipelined execution with no instruction fetch overhead) and program it onto reconfigurable hardware. They make sense when your model has operations CPUs and NPUs do not support, when latency requirements exceed even what an NPU can deliver, or when you genuinely need to update accelerator logic in the field. The downside is cost ($20–200 for embedded-grade parts), power (500 mW to several watts during inference), and development effort. FPGA design requires HDL expertise (Verilog or VHDL) most embedded software engineers do not have, and development time is months rather than weeks.

A concrete comparison: deploying a YOLO object-detection model. CPU-only on a Raspberry Pi Zero 2 W at quad-core 1 GHz costs $15, draws 1.5 W, takes 2,500 ms per frame. A Coral Edge TPU paired with the same A53 host costs $60, draws 2 W combined, takes 25 ms per frame — a 100× speedup from the dedicated NPU. A Xilinx Zynq-7020 with a custom YOLO accelerator in fabric costs $150, draws 3 W, takes 15 ms per frame, and required six months of FPGA design and verification to bring up. The Edge TPU is the right answer for almost every commercial deployment of this kind: large speedup over CPU, reasonable power, off-the-shelf availability. The FPGA is faster, but only 1.7× faster than the TPU, at 2.5× the cost, 50% more power, and a development timeline that kills the project's economics. FPGAs are the right answer for research prototypes, niche low-volume applications where NPUs are insufficient and ASIC NRE is unjustifiable, or applications where field-reconfigurable accelerator logic is genuinely required. For most embedded AI deployments, FPGAs are overkill.

![Three small-multiples panels comparing the same YOLO object-detection model on three platforms. Each panel plots three bars: cost in dollars, power in watts, latency in milliseconds per frame on a log axis. Raspberry Pi Zero 2 W CPU-only sits at $15, 1.5 W, 2500 ms (fails real-time). Coral Edge TPU plus A53 host sits at $60, 2 W, 25 ms (marked as the commercial sweet spot with a bold border). Xilinx Zynq-7020 FPGA sits at $150, 3 W, 15 ms (1.7x faster than TPU at 2.5x the cost).](../images/chapter-08-hardware-for-ai-fig-05.png)
*Figure 8.5 — Same YOLO, three platforms. The FPGA wins on latency; the Coral TPU wins on every other dimension. The constraint shape chooses the answer.*

Several integrated AI hardware options are worth knowing by name and rough specification. Cortex-M55 + Ethos-U55 (NXP, ST, Renesas) — microNPU paired with the M55 CPU, 256 KB to 2 MB SRAM, 50–150 mW during inference, $8–15 per unit, mature toolchain (TFLite Micro with the Ethos-U delegate, the Vela optimizer for quantization and graph transformation), best for keyword spotting, gesture recognition, and small-image classification at 96 × 96 or below. STM32N6 — Cortex-M55 at 800 MHz plus a proprietary NPU at 3 TOPS, 2.5 MB SRAM, 180 mW measured during inference, $12–18 per unit, STM32Cube.AI toolchain, best for vision on MCU including defect detection and gesture recognition. Syntiant NDP120 — an 8-core neural processing array, 1.5 MB on-chip, no general-purpose CPU, designed exclusively for always-on audio AI at under 200 µW, $3–5 per unit, proprietary toolchain (Syntiant Core 2), runs continuously on a coin cell for years but cannot do anything other than audio. Kendryte K210 — RISC-V dual-core at 400 MHz with a 64-MAC convolution accelerator (KPU), 8 MB SRAM, 300 mW during inference, $6–8 per unit, hobbyist-grade tooling and limited TensorFlow support, popular in education and prototyping but not for commercial products.

| Device | NPU type | Best for | Power | Cost | Toolchain |
|---|---|---|---|---|---|
| Cortex-M55 + Ethos-U55 | microNPU | audio, sensors | 50–150 mW | $8–15 | mature |
| STM32N6 | microNPU | vision on MCU | 180 mW | $12–18 | medium |
| Syntiant NDP120 | audio NPU | always-on voice | 0.2 mW | $3–5 | proprietary |
| Kendryte K210 | vision NPU | hobbyist vision | 300 mW | $6–8 | low |

The decision matrix is a few lines: always-on voice at ultra-low power → Syntiant. General-purpose inference on MCU with mature tooling → Cortex-M55 + Ethos-U55. Vision on MCU with the highest performance → STM32N6. Cost-sensitive hobbyist or educational vision → K210. None of these is universal.

![Log-log scatter of effective int8 throughput in GOPS against active power in mW. Six labeled points: a CMSIS-NN Cortex-M7 baseline at 50 mW and 0.2 GOPS, Syntiant NDP120 at 0.2 mW and 0.6 GOPS, K210 at 300 mW and 0.5 GOPS, four Ethos-U55 variants tracing a dashed line at 50 to 150 mW and 32 to 256 GOPS, and STM32N6 at 180 mW and 3000 GOPS. Three diagonal dashed iso-efficiency lines mark 0.01, 1, and 100 TOPS per watt.](../images/chapter-08-hardware-for-ai-fig-06.png)
*Figure 8.6 — TOPS/W efficiency. Move up the chart by adding MACs; move left by killing overhead. Diagonals are constant efficiency.*

The harder skill is knowing when *not* to use an accelerator. There are five recurring cases. *The model is too small to benefit*: a 10,000-parameter model running in 5 ms on a Cortex-M4 will not get faster from an NPU because the overhead of moving data to the accelerator, configuring it, and moving results back exceeds the time saved. *The operations don't map*: if your model is mostly custom layers, dynamic control flow, or sparse operations, the accelerator handles maybe 20–30% of the workload, the CPU runs the rest, and the speedup is negligible. Profile the model first; if the bottleneck is in unaccelerated operations, the accelerator is wasted silicon. *The CPU is fast enough*: if a Cortex-M7 at 480 MHz with CMSIS-NN already meets your latency, adding an NPU is cost without benefit — the simpler CPU solution wins. *The accelerator's power exceeds the CPU's for short workloads*: an NPU drawing 150 mW for 10 ms uses 1.5 mJ; a CPU drawing 30 mW for 40 ms uses 1.2 mJ. The CPU uses less *energy* despite being slower, and for battery-powered low-duty-cycle systems, energy-per-inference is what determines battery life. *Toolchain immaturity*: a proprietary accelerator with poor documentation, limited model support, and buggy code generation can cost more in debugging time than it saves in inference time. Unless the performance gain is transformative — 10× or more — stick with the CPU and standard tools.

The decision workflow is short: profile the model on the CPU with optimized kernels (CMSIS-NN, XNNPACK), measure whether the CPU meets latency, power, and cost requirements; if it does, stop, do not add complexity; if it does not, identify the bottleneck operation, check whether an available accelerator supports it, estimate the realistic speedup including fallback operations, compare cost and power and development time. Only when the accelerator's benefits exceed its costs should you use it. *Acceleration is a tool, not a goal.* The goal is meeting the application's constraints with the simplest, cheapest solution that works.

To make this concrete: a 96 × 96 image classifier for defect detection on a manufacturing line. Model: 400,000 parameters int8, 35 M MACs, 95% accuracy. Application: ≤50 ms latency, <500 mW average, <$15 per unit, 50,000 units per year. STM32H7 (Cortex-M7 at 480 MHz, CPU-only with CMSIS-NN): 180 ms latency, 400 mW, $6 per unit. Fails latency by 3.6× — even with perfect optimization the CPU cannot run this model fast enough. STM32N6 (Cortex-M55 + NPU at 3 TOPS): 42 ms latency, 650 mW, $14 per unit. Meets latency. Exceeds power budget by 30%, but if the system is mains-powered and only thermally limited, 650 mW may be acceptable on thermal analysis. Cost is within budget. Viable. Raspberry Pi Compute Module 4 (quad Cortex-A72 at 1.5 GHz with NEON): 8 ms latency, 2,500 mW, $35 per unit. Latency is excellent, but power is 5× over budget and cost is 2.3× over. Not viable.

Option B is the only viable answer. The NPU's 4× speedup over the CPU is the difference between a product that works and one that does not. *But change the application's latency requirement to 100 ms instead of 50 ms, and Option A becomes viable* — 180 ms is close enough that further model reduction (smaller architecture, better quantization, layer fusion) could bring it under 100 ms. In that case, the $6 CPU-only part beats the $14 NPU part by $400,000 in BOM cost across 50,000 units. The constraint shape determines the answer. The accelerator is justified when it is the cheapest path through the constraints, and not before. The next chapter shifts from local hardware to the network: when does inference belong on the device, and when does it belong on a server somewhere else?

---

## LLM Exercise — Chapter 8: Hardware for AI

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** An accelerator decision module — given a model and a target without an NPU, evaluate whether moving to an accelerator-equipped target closes the budget and at what cost.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/accelerator.py to the tinyml-feasibility toolkit.

Frozen AcceleratorDecision dataclass:
- baseline_target: Target (current pick, CPU-only)
- baseline_verdict: dict (combined memory+compute+power verdict from prior modules)
- candidate_targets: list[Target] (TARGETS where has_accelerator=True)
- candidate_verdicts: list[dict]
- recommendation: Literal["KEEP_BASELINE", "UPGRADE_TO_NPU", "INSUFFICIENT_DATA"]
- recommended_target: Target | None
- justification: str (one paragraph naming the constraint that decided)
- to_markdown() emits an Acceleration section matching Chapter 14's shape

Public function:
`assess_accelerator_benefit(model: ModelSummary, baseline_target: Target, app: Application) -> AcceleratorDecision`

Implementation:
- Run assess_memory + assess_compute + assess_power on baseline_target. If all three FIT, recommendation = KEEP_BASELINE (do not add complexity for benefit you don't need).
- If any baseline verdict is FAILS or TIGHT, evaluate every accelerator-equipped target in TARGETS.
- For NPU targets, override profiling.predict_inference_ms to use accelerator_tops × accelerator_utilization (default 0.6 — the realistic fraction; document why in code comments). Operations not supported by the NPU fall back to CPU; the prompt should document the NPU-supported ops list per target.
- Score each candidate: must satisfy all three verdicts (memory, compute, power) AND be within app.bom_ceiling_usd.
- Recommend the cheapest qualifying target. If none qualify, recommendation = INSUFFICIENT_DATA with justification.

CLI:
- `tinyml-feasibility check-accelerator --app <yaml> --target <baseline> --model <path>` prints AcceleratorDecision

Tests:
- test_keep_baseline_when_cpu_fits — small model + STM32H7, expect KEEP_BASELINE
- test_upgrade_when_compute_fails — heavy model + STM32L4R5, expect UPGRADE_TO_NPU with STM32N6 (or equivalent in TARGETS) recommended
- test_no_qualifying_npu_within_bom — set bom_ceiling_usd low, expect INSUFFICIENT_DATA
```

---

**What this produces:** `tinyml-feasibility check-accelerator --app jaguar.yaml --target STM32L4R5 --model jaguar_dscnn.tflite` evaluates whether the baseline closes the budget; if not, names the cheapest accelerator-equipped target that does. Implements the chapter's "acceleration is a tool, not a goal" rule directly.

**How to adapt this prompt:**
- *For your own project:* The accelerator_utilization default of 0.6 is conservative. Tune it for your target by running real benchmarks.
- *For ChatGPT / Gemini:* Works as-is. Both will overstate NPU speedup — pin them to "realistic utilization, not vendor peak TOPS."
- *For Claude Code:* Best fit.
- *For a Claude Project:* Add the NPU-supported-ops table to the system prompt once; it's stable across chapters 8–13.

**Connection to previous chapters:** Aggregates verdicts from chapters 5 (memory), 6 (compute), 7 (power) and decides at the system level. Begins the cross-cutting integration that Chapter 14 will close.

**Preview of next chapter:** Chapter 9 adds `comms.py` — when does inference belong on-device, on a gateway, or in the cloud? Computes the four communication costs (latency, bandwidth, energy, money) per tier.

---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Carver Mead** coined the term "neuromorphic engineering" and built analog circuits that imitated biological neurons in silicon — the deep history of every NPU on the market today.

**Run this:**

```
Who was Carver Mead, and how does his work on neuromorphic engineering and analog VLSI connect to today's NPUs and AI accelerators? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"Carver Mead"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain what "neuromorphic" means in plain language, with one analog circuit example
- Ask it to compare Mead's analog approach to a digital NPU like the Ethos-U55 or Syntiant NDP120
- Add a constraint: "Answer in the form of a footnote in a hardware-for-ML textbook"

What changes? What gets better? What gets worse?
