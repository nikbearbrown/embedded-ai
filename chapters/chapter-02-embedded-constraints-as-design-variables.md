# Chapter 2 — Embedded Constraints as Design Variables

The skill the previous chapter ended on — being able to look at a model and a hardware target and decide, with numbers, whether they can live together — depends on being able to read a datasheet for what it does not directly say. Datasheets are not written for AI deployment. They were written when the question being asked was *can this part run a PID loop and a UART at the same time*, and they answer that question well. The numbers you need for AI are the same numbers that have always been there. The questions you ask of them are different.

This chapter is about that translation. There is no new physics in it. There is also nothing in it you cannot already do, separately, with the parts of embedded engineering you have. The only new thing is putting the questions in the order that AI deployment requires.

Start with memory.

A neural network is a data structure. Weights, biases, layer configurations, intermediate buffers. All of it has to live somewhere in the device's memory, and *somewhere* is not a single number. Embedded memory comes in regions, and where data lives determines what it can do. The question is not *does the model fit*; it is *does the model fit in the right kind of memory, with enough headroom for the rest of the system*.

Take the nRF52840, a popular Bluetooth Low Energy microcontroller. The datasheet says 1 MB of flash and 256 KB of RAM. At first glance that sounds generous. Now read it through the lens of inference.

Flash is non-volatile, abundant, slow, and read-only at runtime. It is where the model's weights live, baked into the firmware binary at build time. A model with 300,000 parameters stored as 32-bit floats is 1.2 MB — over budget on this part before you have shipped a single line of application code. Quantize the same model to 8-bit integers and it becomes 300 KB, which fits comfortably alongside the firmware and leaves room for the rest of the build.

RAM is volatile, fast, writable, and scarce. It is where the *activations* live during inference — the intermediate tensors that flow from one layer to the next. Activations are not the weights. They are the working memory of the forward pass, and they have to coexist with the application heap, the application stack, the RTOS, and any communication stack the part is also running. The Bluetooth stack on the nRF52840 takes 20–40 KB depending on configuration. If the model's activation buffer is 180 KB and the BLE stack is 30 KB, you have 46 KB of RAM left for everything else. Workable, but tight. If the activation buffer is 200 KB, the deployment fails on RAM even though the model itself "fits" in total memory.

External memory complicates the picture. Some parts — the ESP32-S3 is the canonical example — support external PSRAM up to 32 MB through the package. That dramatically increases what is *addressable*, but external memory is slower than on-chip SRAM and costs more energy per access. Move activations to external PSRAM and every layer reads inputs from across an external bus and writes outputs back across the same bus, which inflates both latency and energy. The model still runs. It just runs differently.

![nRF52840 memory map with side-by-side stacked bars. Left: 1 MB flash split into ~250 KB firmware, 300 KB int8 weights, and ~474 KB free, plus a dashed ghost bar marking the 1.2 MB float32 weights case as over budget. Right: 256 KB SRAM split into 30 KB BLE stack, 180 KB activation arena, and 46 KB remaining headroom.](../images/chapter-02-embedded-constraints-as-design-variables-fig-01.png)
*Figure 2.1 — nRF52840 memory map: where weights and activations actually live.*

So memory is not a hard wall — it is a trade-off surface. To answer it for any candidate hardware you need two numbers from the model (weights size, activation size) and three numbers from the part (flash, on-chip SRAM, external memory if any), and one from the system (how much memory other functions already consume). Most TinyML frameworks will give you the activation number directly; TensorFlow Lite for Microcontrollers exposes a *tensor arena size* that tells you exactly how much RAM the inference will need. If that number plus everything else exceeds available SRAM, the deployment does not happen.

Compute is the second question, and the gap between *clock speed* and *useful neural-network throughput* is the gap most engineers underestimate the first time.

Clock speed tells you cycles per second. It does not tell you multiply-accumulates per second. The ratio between the two depends on the instruction set, the pipeline, whether there is hardware floating-point or integer multiply-accumulate, whether SIMD lanes exist and whether your code uses them, and how much of the cycle budget gets eaten by memory access, instruction fetch, and pipeline stalls. A Cortex-M4 at 100 MHz with an FPU has a theoretical peak of 100 MMAC/s for single-precision floats; a realistic sustained number is closer to 60–70 MMAC/s once you account for memory traffic and the code not being perfectly tight. The same core, running 8-bit integer code with the ARM DSP/SIMD extensions, can hit several times that — *if* the code is written to use them, which is not automatic.

Compare three real targets. The STM32F411 (Cortex-M4 at 100 MHz, with FPU): about 60–70 MMAC/s sustained for float32. The STM32H7A3 (Cortex-M7 at 280 MHz, larger caches, deeper pipeline, double-precision FPU): about 180–220 MMAC/s sustained. The Raspberry Pi Zero 2 W (quad Cortex-A53 at 1 GHz with NEON): on int8, optimized, several giga-ops per second. A model that runs 50 million MACs per inference takes roughly 830 ms on the F411, 250 ms on the H7, and 20–30 ms on the Pi. If your latency budget is 100 ms, the F411 is dead before you start, the H7 is plausible if you can hit your sustained throughput, and the Pi is comfortable — but you have just paid for it in power and complexity.

The arithmetic you need is straightforward. Get the operation count from the model — most frameworks report it; for fully connected layers it is *(input size) × (output size)*, and for convolutions it is *(output H) × (output W) × (output channels) × (kernel H) × (kernel W) × (input channels)*. Get the sustained throughput from a benchmark or by profiling. Divide. *Inference latency = total operations / sustained throughput.* If a vendor claims 400 GOPS for some "AI acceleration" mode, trust the claim only after multiplying by a utilization factor (typically 0.5–0.7) for what real code on a real model achieves, and only after profiling on hardware. Marketing numbers describe the silicon; profiling numbers describe your model.

![Horizontal bar chart on a log-spaced latency axis. Three rows: RPi Zero 2 W at about 25 ms (clears budget), STM32H7A3 at about 250 ms (plausible with int8 and SIMD), STM32F411 at about 830 ms (misses budget by eight times). A dashed vertical line marks the 100 ms budget; bars to the left clear it, bars crossing it fail.](../images/chapter-02-embedded-constraints-as-design-variables-fig-02.png)
*Figure 2.2 — Inference latency for a 50 M-MAC model across three targets vs a 100 ms budget.*

Power is the third question, and it is usually the binding one for battery-powered devices.

Power is not a single number. It is a profile that varies with operating mode, clock, peripheral activity, and duty cycle. A part running inference draws one current. The same part with peripherals on but the CPU asleep draws a different current. The same part in deep sleep draws a third, much smaller current. The total energy consumed is the integral of that profile over time, and average power is the time-weighted sum:

$$
I_{\text{avg}} = \frac{I_{\text{active}} \cdot t_{\text{active}} + I_{\text{idle}} \cdot t_{\text{idle}}}{t_{\text{active}} + t_{\text{idle}}}
$$

Take a wearable activity tracker on an nRF52840. Inference runs every five seconds and takes 80 ms; the rest of the time the part is in idle mode. Datasheet currents: 5.3 mA active, 2.8 µA idle. The sum runs as

$$
I_{\text{avg}} = \frac{5.3\ \text{mA} \cdot 0.08\ \text{s} + 0.0028\ \text{mA} \cdot 4.92\ \text{s}}{5\ \text{s}} \approx 0.088\ \text{mA}.
$$

A 220 mAh coin cell at that draw lasts about 2,500 hours — 104 days — well beyond the two-week target.

Now suppose accuracy demands push the model deeper and inference latency doubles to 160 ms. Same arithmetic gives 0.172 mA average and about 53 days of battery — still fine.

Now suppose the application changes and inference has to run every second to catch shorter activities. Same 160 ms inference, same currents, new duty cycle:

$$
I_{\text{avg}} = \frac{5.3\ \text{mA} \cdot 0.16\ \text{s} + 0.0028\ \text{mA} \cdot 0.84\ \text{s}}{1\ \text{s}} \approx 0.85\ \text{mA}.
$$

The coin cell now runs about 259 hours, eleven days, which is below the two-week threshold. The deployment fails on power. Notice what changed: the model did not change, the hardware did not change, the firmware did not change. The application asked the inference to run more often. That is the entire delta, and it is enough to take the device out of spec.

![Three side-by-side current-vs-time strips for the nRF52840 wearable. Case A: 80 ms active pulse inside a 5 s period, I_avg about 0.088 mA, 104 days, passes. Case B: 160 ms active pulse inside a 5 s period, I_avg about 0.172 mA, 53 days, passes. Case C: 160 ms active pulse inside a 1 s period, I_avg about 0.85 mA, 11 days, fails. Below the strips, a log-scaled days axis places all three cases against a dashed two-week threshold; Case C falls below it.](../images/chapter-02-embedded-constraints-as-design-variables-fig-03.png)
*Figure 2.3 — Duty cycle decides battery life: same hardware, same model, three deployments.*

Power couples to memory and to compute, and the coupling matters. Reducing inference latency by clocking faster increases active current. Moving activations to external PSRAM saves on-chip RAM but every external access costs more energy than an on-chip access, so power goes up. Quantizing to int8 reduces bytes moved per operation, which reduces both cycles and the energy per cycle. Every optimization that improves one constraint touches the others.

![Four-node diagram with memory, compute, power, and real-time at the corners. Curved arrows along each edge carry annotations: int8 quantize reduces bytes and cycles, larger model raises activation RAM, PSRAM adds energy per access, int8 weights cut flash and energy, dynamic graph raises WCET variance, deadline tightening forces faster code, clock-faster raises active current, cache misses raise WCET variance, peak current spike causes brown-out, lock to TCM cuts WCET at area cost.](../images/chapter-02-embedded-constraints-as-design-variables-fig-04.png)
*Figure 2.4 — The four constraints are a connected surface, not independent axes.*

Power also has a peak constraint, distinct from average. A coin cell with 220 mAh capacity is not the same as a coin cell that can deliver 10 mA on demand. CR2032 cells, for instance, have high internal resistance — the maximum sustained current is on the order of 3 mA, and inference routines that draw more than that pull the supply voltage down, brown-out the part, and reset the system. The fix is a larger battery, a bulk capacitor sized to supply the peak, a slower clock, or a longer inference spread over more cycles. Average power tells you how long the device runs. Peak power tells you whether it runs at all.

Real-time is the fourth question, and the thing it tests is not how fast inference runs on average — it is how slow it can possibly run.

A real-time system is one whose correctness depends on *when* a result arrives, not just on *what* the result is. Soft real-time tolerates the occasional late result. Hard real-time does not — a missed deadline is a system failure. Most embedded AI is soft real-time: a smart thermostat with a slow inference is a slow thermostat, not a broken one. Some embedded AI is hard real-time: a motor controller that uses inference to detect bearing faults has a window during which the alert can prevent damage and after which the damage is done. A medical device that detects arrhythmia has a window during which therapy is effective.

Inference is hard to bound. Execution time depends on the input data (some paths short-circuit, some trigger expensive branches), on cache state (whether weights and activations are resident), on memory contention (other tasks or DMA competing for the bus), and on interrupt latency (whether something else can preempt the inference). Worst-case execution time analysis for traditional embedded code is mature, with tools that model pipelines and caches. WCET for neural network code is an active research area without settled practice — the code is large, library-heavy, and full of dynamic patterns.

The pragmatic approach for hard real-time is to make the problem easier rather than to solve the harder version. Use a fixed-point or integer-only network with no dynamic control flow so every layer does the same work regardless of input. Disable interrupts during inference, or run inference at the highest priority so it cannot be preempted. Lock weights and activations into tightly coupled memory so cache misses are not part of the worst case. Profile inference on adversarial inputs that try to elicit the worst case, then add safety margin — typically 20–50% over the measured maximum — and treat the result as the WCET. If you cannot bound the worst case to the deadline with margin, you do not deploy in hard real-time.

A worked example pulls all four questions together.

You are designing a smart-agriculture sensor that takes a 96×96 RGB image every ten minutes, classifies it as healthy / diseased / pest-damaged with an on-device model, and reports results over LoRaWAN once per hour. The whole device must run six months on a 5,000 mAh battery; solar charging is not available because the sensor sits under a tree canopy. You have a MobileNetV2-based classifier with 300,000 parameters (1.2 MB float32, 300 KB int8) and 45 million MACs per inference. Profiled activation memory is 200 KB. Three candidate platforms.

| Platform | Core | Clock | SRAM | Flash | AI accel | Active I | Sleep I | Cost |
|---|---|---|---|---|---|---|---|---|
| ESP32-S3 | Dual Xtensa LX7 | 240 MHz | 512 KB | 8 MB | vector inst., ~400 GOPS claimed | 40 mA | 10 µA | $4.50 |
| STM32L4R5 | Cortex-M4 + FPU | 120 MHz | 640 KB | 2 MB | none | 12 mA | 0.4 µA | $6.00 |
| RPi Zero 2 W | Quad Cortex-A53 | 1 GHz | 512 MB LPDDR2 | (SD card) | NEON SIMD | ~150 mA idle | n/a | $15.00 |

Memory is fine on all three — 300 KB of int8 weights and 200 KB of activations fit comfortably in every option's RAM and flash. Memory is not the binding constraint here.

Compute is also fine on all three for this duty cycle. The ESP32-S3, on its claimed acceleration, computes 45 M MACs in roughly 100–300 ms in practice. The STM32L4R5 at 120 MHz with FPU sustains around 70 MMAC/s for float32, so float inference is about 640 ms; int8 with SIMD roughly halves that. The Pi handles it in under 10 ms with NEON. The application asks for one inference every ten minutes, so any of these is far inside the latency budget.

Power is where the platforms separate. Inference takes about 0.3 s per ten-minute cycle, so the active duty cycle is 0.3 / 600 = 0.05%. For the ESP32-S3:

$$
I_{\text{avg}} = \frac{40\ \text{mA} \cdot 0.3\ \text{s} + 0.01\ \text{mA} \cdot 599.7\ \text{s}}{600\ \text{s}} \approx 0.03\ \text{mA}.
$$

5,000 mAh at 0.03 mA is about 19 years, which says less about the ESP32-S3 than about how completely the sleep current dominates when the active duty cycle is this small.

For the STM32L4R5, lower active current and far lower sleep current give an even smaller average — fractions of a microamp once you actually do the integration honestly — and battery self-discharge and LoRaWAN transmit overhead become the binding terms long before the part itself runs out of power.

For the Raspberry Pi Zero 2 W, there is no true deep-sleep mode. Best case it idles at around 150 mA. At 150 mA continuous, 5,000 mAh runs out in about 33 hours. Even with aggressive optimization to 50 mA idle, battery life is on the order of four days. Six months is not on the table. The Pi disqualifies itself on power, not on compute or memory.

![Four-axis radar chart comparing ESP32-S3, STM32L4R5, and RPi Zero 2 W. Axes: memory headroom, compute margin, battery life on a log scale with a six-month target marker, and inverse cost score. The two microcontroller polygons cover broadly similar viable regions. The Pi polygon stretches to the outer ring on memory and compute but collapses to near the center on the battery axis, marking a failure even though the other axes pass.](../images/chapter-02-embedded-constraints-as-design-variables-fig-05.png)
*Figure 2.5 — Three candidates, four axes: the Pi collapses on power while two MCUs occupy the viable region.*

So the choice collapses to ESP32-S3 versus STM32L4R5. Both meet all constraints. The STM32 has lower cost and lower active power; the ESP32 has the AI accelerator and a richer software ecosystem if the model needs to grow. The decision moves to secondary factors — toolchain familiarity, camera-interface support, LoRaWAN library quality, and whether you trust the ESP32's claimed acceleration enough to bet a six-month deployment on it without profiling first. None of those factors will let you change the four answers above. The constraints define the set of viable platforms; the secondary factors decide which of the viable platforms is the right one.

That is what *constraints as design variables* means. Memory, compute, power, real-time — each is a number you can compute from the datasheet and the model. Together they are a four-dimensional surface, and the deployment lives at the points on the surface where all four are satisfied at once. Most points on the surface are not such points. The job of the next chapter is to give you the model side of the equation — what makes inference cheap or expensive, what an architecture's resource demand actually depends on — so the calculations in this chapter have something on the other side of the equals sign.

![Sequential four-gate flowchart. Diamonds across the top, left to right: memory (weights fit flash, arena plus system under SRAM), compute (ops over sustained throughput under latency budget), power (average and peak current within battery and supply limits), real-time (WCET plus margin under deadline). A yes path links them across the top and terminates in a viable deploy box. A no path drops each gate into a model-side iteration box listing quantize, prune, raise clock, stretch duty cycle, or lock to TCM, each looping back. A footer bar states that if no iteration closes the gap, the part or requirement changes.](../images/chapter-02-embedded-constraints-as-design-variables-fig-06.png)
*Figure 2.6 — Decision flowchart: does this model deploy on this part?*

---

## LLM Exercise — Chapter 2: Embedded Constraints as Design Variables

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** A `Target` dataclass with a real microcontroller catalog, and a `Constraints` translator that converts `Application` + `Target` into the four-constraint object the toolkit reasons over.
**Tool:** Claude Code

---

**The Prompt:**

```
Extend the tinyml-feasibility package (chapter 1 set up the scaffold and Application).

Add two modules:

1. src/tinyml_feasibility/target.py
 Frozen Target dataclass with fields: name, core (e.g., "Cortex-M4"), clock_mhz, sram_kb, flash_kb, active_current_ma_per_mhz, sleep_current_ua, has_accelerator (bool), accelerator_tops (float, 0.0 if none), cost_usd.
 Provide a TARGETS dict mapping name → Target instance, populated from datasheets for at least: STM32L4R5, STM32H743, STM32N6, nRF52840, ESP32-S3, RPi-Zero-2W, Arduino-Nano-33-BLE-Sense.
 Every numeric value gets a comment with the datasheet URL it came from. NO FABRICATION — if a number can't be sourced, leave it None and emit a warning.

2. src/tinyml_feasibility/constraints.py
 Constraint dataclass: category (Literal["memory","compute","power","real_time"]), axis (str, e.g., "sram_kb", "latency_ms"), budget (float | str), source (str pointing to where the budget came from, e.g., "application.memory_budget.sram_kb").
 Function `derive_constraints(app: Application, target: Target) -> list[Constraint]` produces one Constraint per axis: memory:flash, memory:sram, compute:latency, power:average, real_time:class.

CLI extension:
- `tinyml-feasibility list-targets` prints each Target as a table (name, core, clock, sram, flash, sleep current, cost)
- `tinyml-feasibility constraints --app <yaml> --target <name>` prints the derived Constraint list with sources

Tests:
- test_target_lookup — TARGETS["STM32L4R5"] returns a Target with sleep_current_ua < 1.0
- test_constraints_derived — for the example app + STM32L4R5, derive_constraints returns exactly 5 Constraint instances covering all four categories
- test_constraints_traceable — every Constraint.source is a non-empty string

Run pytest. All tests pass before you stop.
```

---

**What this produces:** A microcontroller catalog (with traceable datasheet citations) and a translator that turns application requirements + target into the structured Constraint list the toolkit will use everywhere downstream.

**How to adapt this prompt:**
- *For your own project:* Add your target board to TARGETS by reading its datasheet. Note Claude is good at extracting datasheet numbers but verify each one against the source PDF before committing.
- *For ChatGPT / Gemini:* Works as-is.
- *For Claude Code:* Use `--allowed-tools edit,bash,web_search` so it can pull datasheet values. Always sanity-check the citations before merging.
- *For a Claude Project:* Add the Target dataclass schema to the system prompt; this saves chapters 5–10 from re-deriving it.

**Connection to previous chapters:** Chapter 1's `Application` is now consumed alongside `Target` by `derive_constraints`. The four-constraint object becomes the contract every later module reads.

**Preview of next chapter:** Chapter 3 adds `model.py` to load a TFLite model file and extract parameter count, MAC count, layer types, and the largest activation tensor — the inputs every memory/compute/power module will need.

---

## Prompts

Use these prompts with Claude to generate interactive D3 v7 versions of the
figures in this chapter. Each produces a standalone HTML file you can open
in a browser and modify freely.

**Prerequisites:** Load `brutalist/CLAUDE.md` and `brutalist/DESIGN.md` into
your Claude project context before using these prompts. They define the stack,
naming conventions, color system, and typography the figures use.

---

### Figure 2.1 — nRF52840 memory map under inference

Build a two-panel D3 v7 figure showing two stacked vertical bars side by side. Left panel: 1 MB flash budget for the nRF52840, with segments for firmware (250 KB), int8 weights (300 KB, primary emphasis), and remaining free flash (~474 KB). Add a dashed ghost bar next to the stack representing the 1.2 MB float32 weights case, labeled "over budget" in `var(--color-red)`. Right panel: 256 KB SRAM budget, with segments for BLE stack (30 KB), activation arena (180 KB, primary emphasis), and remaining headroom (46 KB). Each segment carries an inline label with its name and KB value. y-axis ticks in KB; zero baseline on both panels. Tooltip on each segment shows segment name and KB. Standalone HTML, D3 v7 from the pinned CDN, inline CSS using `var(--color-*)`, EB Garamond / Inter / JetBrains Mono fonts, `prefers-color-scheme: dark` support, ResizeObserver redraw, role="img" with title and desc.

> Reference implementation: `d3/chapter-02-embedded-constraints-as-design-variables-fig-01.html`

---

### Figure 2.2 — Inference latency across three embedded targets

Build a single horizontal bar chart on a log-scaled x-axis. Three rows: RPi Zero 2 W (25 ms, `var(--color-ink)`, "comfortable"), STM32H7A3 (250 ms, `var(--color-secondary)`, "plausible with int8/SIMD"), STM32F411 (830 ms, `var(--color-red)`, "misses budget by 8×"). x-domain `[10, 1000]` ms with log-spaced tick values at 10, 30, 100, 300, 1000. Overlay a dashed vertical line at 100 ms labeled "100 ms budget" in `var(--color-ochre)`. Each bar carries its value and a one-line verdict at the bar end. Left-axis labels show target name and a one-line core/clock subtitle. Tooltip on hover. Standalone HTML, D3 v7, inline CSS with CSS variables, EB Garamond / Inter / JetBrains Mono, dark-mode media query, ResizeObserver redraw, accessible markup.

> Reference implementation: `d3/chapter-02-embedded-constraints-as-design-variables-fig-02.html`

---

### Figure 2.3 — Duty cycle decides battery life

Build a three-panel figure plus a summary log strip below. Each top panel is a current-vs-time strip for an nRF52840 wearable case: Case A (80 ms active / 5 s period, I_avg ≈ 0.088 mA, 104 days, passes), Case B (160 ms / 5 s, I_avg ≈ 0.172 mA, 53 days, passes), Case C (160 ms / 1 s, I_avg ≈ 0.85 mA, 11 days, fails). Each strip shows a tall narrow rectangle for the active pulse and a thin baseline for idle. Fail case uses `var(--color-red)`; passing cases use `var(--color-ink)`. Below the strips, a single log-scaled days axis from 1 to 1000 with dot markers for the three cases at 104, 53, and 11 days, and a dashed line at 14 days labeled "2-week threshold" in `var(--color-red)`. Tooltip on pulse and on each dot. Standalone HTML, D3 v7, CSS variables, EB Garamond / Inter / JetBrains Mono, dark-mode and reduced-motion media queries, ResizeObserver redraw, accessible markup.

> Reference implementation: `d3/chapter-02-embedded-constraints-as-design-variables-fig-03.html`

---

### Figure 2.4 — Four-constraint coupling diagram

Build a single-panel node-link diagram. Four ellipse nodes at the corners of an implicit square: memory (top-left), compute (top-right), power (bottom-left), real-time (bottom-right). Each node fill is `var(--color-ink)`, labels in `var(--color-white)`. Draw ten directed curved arrows between nodes (both directions on each edge plus two diagonals), each carrying a short labeled trade-off such as "int8 quantize → −bytes, −cycles", "clock faster → +active current", "PSRAM → +energy/access", "lock to TCM → −WCET, +area". The clock-faster diagonal is highlighted in `var(--color-red)`. Hover on any edge highlights the arrow and label and shows a tooltip naming the source-to-target pair. Standalone HTML, D3 v7, CSS variables, EB Garamond / Inter, dark-mode media query, ResizeObserver redraw, role="img" with title and desc.

> Reference implementation: `d3/chapter-02-embedded-constraints-as-design-variables-fig-04.html`

---

### Figure 2.5 — Radar comparison of three candidate platforms

Build a four-axis radar chart with axes for memory headroom (top), compute margin (right), battery life on a log scale (bottom), and inverse cost score (left). Plot three overlapping polygons normalized to `[0, 1]` per axis: ESP32-S3 (`var(--color-red)`, viable), STM32L4R5 (`var(--color-ink)`, viable, dashed stroke), RPi Zero 2 W (`var(--color-secondary)`, fails on battery, dotted stroke). Concentric polygon rings at 0.25, 0.50, 0.75, 1.00. Mark the six-month battery target on the battery axis with a red circle and label "6-mo target". Right-side legend listing each platform with cost, projected life, and pass/fail. Tooltip on each polygon vertex showing platform name and axis score. Standalone HTML, D3 v7, CSS variables, EB Garamond / Inter / JetBrains Mono, dark-mode media query, ResizeObserver redraw, accessible markup.

> Reference implementation: `d3/chapter-02-embedded-constraints-as-design-variables-fig-05.html`

---

### Figure 2.6 — Deployment decision flowchart

Build a horizontal flowchart of four sequential gate diamonds: memory, compute, power, real-time. Each diamond carries the gate name and the two questions it asks (e.g., "weights fit flash? arena+system < SRAM?"). The yes branch links each gate to the next along the top in `var(--color-ink)` and terminates in a "VIABLE — deploy" box after gate four. The no branch drops each gate down to a model-side iteration box in `var(--color-red)` listing three concrete actions (e.g., "quantize weights", "prune layers", "shrink activations") and a "→ retry from gate N" line. Below the iteration row, a footer bar reads "if no iteration closes the gap — change the part, change the model class, or change the requirement". Clicking a gate highlights it in `var(--color-red)`. Tooltip on hover. Standalone HTML, D3 v7, CSS variables, EB Garamond / Inter, dark-mode and reduced-motion media queries, ResizeObserver redraw, accessible markup.

> Reference implementation: `d3/chapter-02-embedded-constraints-as-design-variables-fig-06.html`

---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Lynn Conway** co-wrote the textbook that turned chip design from black art into a set of design rules — turning silicon constraints into variables you could reason about, decades before tinyML.

**Run this:**

```
Who was Lynn Conway, and how does her work on VLSI design methodology with Carver Mead connect to treating hardware constraints as design variables? Three paragraphs. End with the single most surprising thing about her career.
```

→ Search **"Lynn Conway"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain "design rules" in chip design as if you've never seen a circuit
- Ask it to compare Conway's VLSI revolution to today's struggle to make embedded ML deployment systematic
- Add a constraint: "Answer in the form of a single page from a 1980s engineering textbook"

What changes? What gets better? What gets worse?
