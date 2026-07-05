# Bear's Doodles — Embedded AI Video Ideas

*Ordered by chapter (per request), not by score. 22 candidates from chapters 1–14. Intro, appendices, and the themes chapter yielded no distinct video zones.*

## Candidate 01 — Why a Perfect AI Model Killed the Doorbell
- Source: `embedded-ai/chapters/01-chapter-when-ai-meets-constrained-hardware.md`
- Production mode: Mixed
- Hook: The model was accurate, the hardware worked, the firmware shipped — and the product still died in the field.
- Core idea: Inference time times inference frequency sets a duty cycle, and duty cycle times active current sets battery life — a number you can compute before shipping, and nobody did.
- Visual object: A cascading budget waterfall (memory → latency → power) where the final power bar falls short of the target line
- Manim move: scan
- Short-form fit: Strong
- Prerequisites: battery capacity (mAh), what inference is
- Exclusions: no Target A/B cost comparison, no edge-vs-cloud four reasons, no FPU-emulation detail — one device, one cascade, power is the punchline
- Score: 9/10

## Candidate 02 — Nothing Changed Except How Often — and the Battery Died
- Source: `embedded-ai/chapters/02-chapter-embedded-constraints-as-design-variables.md`
- Production mode: Manim visualization
- Hook: Same model, same hardware, same firmware — battery life fell from 104 days to 11.
- Core idea: Average current is the time-weighted mix of a tall active pulse and a near-zero sleep floor, so shrinking the period between inferences multiplies average power even though every single inference is unchanged.
- Visual object: A current-vs-time strip with one inference pulse per period, the period visibly shrinking
- Manim move: scan
- Short-form fit: Strong
- Prerequisites: current draw, battery capacity
- Exclusions: no I_avg equation derivation, no nRF52840 datasheet detail, no race-to-sleep (that is Candidate 11) — overlap warning: consolidate with Candidate 01 at pick time if both feel like the same lesson
- Score: 8/10

## Candidate 03 — A Battery Can Be Full and Still Crash Your Device
- Source: `embedded-ai/chapters/02-chapter-embedded-constraints-as-design-variables.md`
- Production mode: Manim visualization
- Hook: The coin cell had most of its charge left, and the device browned out and rebooted anyway.
- Core idea: A CR2032's internal resistance caps sustained current around 3 mA, so an inference burst above that drags the supply voltage below the reset threshold — average power says how long the device runs, peak power says whether it runs at all.
- Visual object: A supply-voltage trace sagging past the brown-out line while the inference current spike is live
- Manim move: trace
- Short-form fit: Strong
- Prerequisites: current vs voltage, what a reset is
- Exclusions: no internal-resistance circuit math, no bulk-capacitor sizing, no battery chemistry survey — one spike, one sag, one reboot
- Score: 7/10

## Candidate 04 — Nine Weights vs Nineteen Million
- Source: `embedded-ai/chapters/03-chapter-ml-for-embedded-engineers.md`
- Production mode: Manim visualization
- Hook: Connecting a camera image to just 128 neurons needs nineteen million weights — 76 megabytes — before the network learns anything.
- Core idea: A convolution slides one small filter across the image and reuses the same nine weights at every position, preserving spatial structure while cutting parameters by six orders of magnitude.
- Visual object: A 3×3 filter sliding across an image grid, its nine shared weights highlighted at every stop
- Manim move: scan
- Short-form fit: Strong
- Prerequisites: what a neural-network weight is, image as pixel grid
- Exclusions: no MAC-count formula, no pooling, no CNN architecture tour, no depthwise separable (that is Candidate 05)
- Score: 9/10

## Candidate 05 — Split the Convolution, Pay an Eighth
- Source: `embedded-ai/chapters/03-chapter-ml-for-embedded-engineers.md`
- Production mode: Manim visualization
- Hook: MobileNet's entire trick is doing one convolution as two steps — and paying an eighth of the price.
- Core idea: Filter each channel separately with a small spatial kernel, then mix channels with a 1×1 pointwise pass — 288 + 2,048 multiplications per pixel where the fused operation cost 18,432.
- Visual object: One dense convolution block splitting into a depthwise block and a pointwise block, cost counters ticking under each
- Manim move: split
- Short-form fit: Medium
- Prerequisites: convolution, channels
- Exclusions: no inverted residuals, no MobileNetV2/V3 history, no width-multiplier tuning — one split, one cost comparison
- Score: 7/10

## Candidate 06 — Same Math, Ten Times Slower
- Source: `embedded-ai/chapters/04-chapter-inference-mechanics.md`
- Production mode: Manim visualization
- Hook: Two runs of the exact same multiply count — one takes ten times longer, and the arithmetic isn't the reason.
- Core idea: When operands don't fit near the processor, every fetch from far memory costs more cycles than the multiply itself; blocking the matrix into cache-sized tiles that get reused restores near-peak speed with zero change to the math.
- Visual object: A matrix multiply — rows streaming in from distant memory versus one resident tile being reused many times
- Manim move: compare
- Short-form fit: Strong
- Prerequisites: matrix multiply, idea of a cache
- Exclusions: no roofline model, no arithmetic-intensity formula, no cycle-count tables — one naive pass, one tiled pass, one clock
- Score: 8/10

## Candidate 07 — Predicted 367 ms. Measured 1,200.
- Source: `embedded-ai/chapters/04-chapter-inference-mechanics.md`
- Production mode: Mixed
- Hook: The spec-sheet math promised 367 milliseconds; the first run on real hardware took 1,200 — and both numbers were "right."
- Core idea: The gap between theory and hardware has named, findable causes — reference kernels instead of SIMD kernels, activations spilled to slow external memory, float instead of int8 — and profiling closes them one at a time, down to 45 ms.
- Visual object: A latency waterfall whose bars drop step by step past the 100 ms target line as each fix lands
- Manim move: trace
- Short-form fit: Medium
- Prerequisites: latency, what a build/toolchain is (loosely)
- Exclusions: no DWT cycle-counter code, no per-operator profiling table, no quantization mechanics (Candidate 19) — each fix gets one sentence and one falling bar
- Score: 8/10

## Candidate 08 — The Model Fit in Memory and Crashed Anyway
- Source: `embedded-ai/chapters/05-chapter-memory.md`
- Production mode: Manim visualization
- Hook: 256 KB of RAM, a 180 KB model — simple subtraction says it fits, and it crashes 40 milliseconds into the first inference.
- Core idea: Weights rest in flash, but activations — the intermediate tensors made during inference — need writable RAM while it runs, and their peak, not the parameter count, decides fit; reusing buffers shrinks that peak to the largest tensor alive at any one moment.
- Visual object: Tensors flowing through a layer stack while RAM buffers pile up (naive) and then get recycled (reuse)
- Manim move: accumulate
- Short-form fit: Strong
- Prerequisites: flash vs RAM, layers
- Exclusions: no im2col scratch buffers, no tensor-arena code, no linker maps — the weights/activations distinction and buffer reuse only
- Score: 9/10

## Candidate 09 — The Smaller Model That Was Eighty Times Slower
- Source: `embedded-ai/chapters/06-chapter-compute.md`
- Production mode: Manim visualization
- Hook: The LSTM had fewer parameters than the CNN — and ran nearly eighty times slower.
- Core idea: A recurrent network re-runs its whole computation once per time step, so 14 million MACs per step across 100 steps is 1.4 billion — parameter count measures storage, but ops-per-inference measures time, and recurrence multiplies the second without touching the first.
- Visual object: Time-step boxes unrolling one by one while a cost counter piles up next to a single-pass CNN
- Manim move: accumulate
- Short-form fit: Strong
- Prerequisites: parameters vs operations, sequence data
- Exclusions: no LSTM gate internals, no hidden-state math, no audio-feature pipeline — the unrolling and the multiplication are the whole video
- Score: 7/10

## Candidate 10 — The 4× Speedup Already in Your Chip
- Source: `embedded-ai/chapters/06-chapter-compute.md`
- Production mode: Manim visualization
- Hook: The same chip at the same clock runs the same model four times faster — if the code bothers to ask.
- Core idea: SIMD packs four int8 values into one 32-bit register and processes them in a single instruction, but the free 4× only appears when the build uses optimized kernels — reference C code leaves it on the table silently.
- Visual object: Four byte-lanes merging into one register and executing as one instruction, beside a scalar lane doing four
- Manim move: compare
- Short-form fit: Strong
- Prerequisites: registers/instructions at cartoon level, int8
- Exclusions: no instruction mnemonics, no disassembly, no CMSIS-NN build configuration — lanes and one clock, nothing else
- Score: 7/10

## Candidate 11 — Run Faster to Save Power
- Source: `embedded-ai/chapters/07-chapter-power-and-energy.md`
- Production mode: Manim visualization
- Hook: Doubling the clock raised the current draw seventy-five percent — and the battery lasted longer.
- Core idea: Energy is area under the current curve, and a taller-but-narrower active burst beats a lower-but-longer one because deep sleep is thousands of times cheaper than slowed-down work — so finish fast and race to sleep.
- Visual object: Two current-vs-time traces whose shaded areas (energy) are compared directly
- Manim move: compare
- Short-form fit: Strong
- Prerequisites: current, energy as area under a curve (taught in-video)
- Exclusions: no dynamic-vs-static power split, no DVFS, no crossover analysis for high duty cycles — two traces, two areas, one winner
- Score: 9/10

## Candidate 12 — It's Not the AI Draining the Battery. It's the Radio.
- Source: `embedded-ai/chapters/07-chapter-power-and-energy.md`
- Production mode: Manim visualization
- Hook: The team optimized the neural network for weeks and the battery life barely moved — because inference was never what was eating it.
- Core idea: One radio transmission can cost several times the energy of an inference, so the transmit schedule — not the model — sets the battery ceiling; profile one full duty cycle and the biggest feature in the current trace is the real constraint.
- Visual object: An oscilloscope-style current trace where sleep floor, sensor spike, inference burst, and a dominating radio envelope draw themselves in sequence
- Manim move: trace
- Short-form fit: Strong
- Prerequisites: current trace, duty cycle
- Exclusions: no LoRaWAN protocol detail, no mJ arithmetic tables, no energy-harvesting tangent — one annotated trace, one surprise
- Score: 8/10

## Candidate 13 — Your CPU Spends Two-Thirds of Its Time Not Computing
- Source: `embedded-ai/chapters/08-chapter-hardware-for-ai.md`
- Production mode: Manim visualization
- Hook: On a matrix multiply — the thing processors supposedly do — only thirty percent of the CPU's cycles are arithmetic.
- Core idea: General-purpose flexibility (instruction fetch, cache management, pipeline control) is where the cycles and energy go; an NPU hard-wires the one predictable pattern inference needs, so over ninety percent of its time is arithmetic.
- Visual object: A cycle bar splitting into arithmetic vs overhead segments, CPU beside NPU
- Manim move: compare
- Short-form fit: Strong
- Prerequisites: what a CPU cycle is, matrix multiply
- Exclusions: no MAC-array microarchitecture, no NPU class taxonomy, no vendor parts — two bars and why they differ
- Score: 8/10

## Candidate 14 — Why Your 10× Accelerator Only Made It 3× Faster
- Source: `embedded-ai/chapters/08-chapter-hardware-for-ai.md`
- Production mode: Manim visualization
- Hook: The NPU really is ten times faster than the CPU — and your model only got three times faster.
- Core idea: An accelerator runs only the operations it supports; the twenty percent that falls back to the CPU comes to dominate total time, so realized speedup is set by the model-to-hardware mapping, not by the peak TOPS on the box.
- Visual object: A stream of ops routing into a fast NPU lane and a slow CPU fallback lane, the fallback queue backing up
- Manim move: split
- Short-form fit: Strong
- Prerequisites: what an accelerator is (Candidate 13 helps but not required)
- Exclusions: no Amdahl's-law formula, no Ethos-U55 op tables, no FPGA tangent — the routing picture carries everything
- Score: 8/10

## Candidate 15 — Send the Middle of the Network, Not the Picture
- Source: `embedded-ai/chapters/09-chapter-communication-edge-cloud.md`
- Production mode: Manim visualization
- Hook: The image is 27 kilobytes and the radio can't carry it — but layer six's output is 8 kilobytes and doesn't even look like a picture.
- Core idea: Split inference runs the early layers on-device and ships the small intermediate activations to a server for the rest — less bandwidth than the raw input, full-model accuracy, and partial privacy because activations aren't images.
- Visual object: A layer stack with activation sizes shrinking layer by layer, a dashed cut line dropping at the narrowest point
- Manim move: split
- Short-form fit: Medium
- Prerequisites: layers and activations (Candidate 08 helps), bandwidth
- Exclusions: no four-tier topology tour, no federated learning, no cost arithmetic — find the thin waist, cut there
- Score: 8/10

## Candidate 16 — Make AI Safe by Taking It Out of the Loop
- Source: `embedded-ai/chapters/10-chapter-real-time-ai.md`
- Production mode: Mixed
- Hook: The AI needs 38 milliseconds to answer and the machine must stop in 5 — and the fix is not a faster model.
- Core idea: Run the AI asynchronously as an advisor that writes a fault probability, while a simple deterministic detector inside the 1 kHz control loop holds the hard deadline — the AI improves detection, and the safety guarantee never depends on it.
- Visual object: Three parallel timelines — control-loop ticks, a slow AI inference bar, a fast rule-based trip — against a 5 ms deadline marker
- Manim move: compare
- Short-form fit: Medium
- Prerequisites: deadline, control loop (cartoon level)
- Exclusions: no Uber case retelling, no WCET analysis, no safety-standard alphabet (ASIL/SIL) — one CNC machine, three timelines
- Score: 8/10

## Candidate 17 — Don't Ship the Most Accurate Model
- Source: `embedded-ai/chapters/11-chapter-model-selection.md`
- Production mode: Manim visualization
- Hook: The best model on the leaderboard failed on the device by four kilobytes; the one that shipped was "worse" on every benchmark.
- Core idea: Candidates live on an accuracy-versus-cost frontier — constraints strike out the infeasible and the dominated, and you ship the surviving point with margin, because accuracy is one axis of the decision, not the decision.
- Visual object: A scatter of candidate models on latency–accuracy axes, dominated points struck out, the Pareto frontier tracing itself, constraint lines closing in
- Manim move: trace
- Short-form fit: Medium
- Prerequisites: accuracy, latency budget
- Exclusions: no five-metric profiling checklist, no NAS, no fall-detector candidate-by-candidate walkthrough — the frontier picture is the video
- Score: 7/10

## Candidate 18 — Delete 80% of Your Network and It Runs No Faster
- Source: `embedded-ai/chapters/12-chapter-model-optimization.md`
- Production mode: Manim visualization
- Hook: You pruned four-fifths of the weights, accuracy barely moved — and inference time didn't change at all.
- Core idea: Scattered zeros still live inside a dense matrix that the kernel multiplies in full; only removing whole channels — structured pruning — actually shrinks the matrix, which is why flash, RAM, and latency all drop together or not at all.
- Visual object: A weight matrix — individual cells zeroing out (dimensions unchanged) versus whole channel rows sliced away (matrix visibly shrinks)
- Manim move: compare
- Short-form fit: Strong
- Prerequisites: weights as a matrix, what pruning claims to do
- Exclusions: no sparse-format (CSR) detail, no iterative prune–fine-tune loop, no accuracy-vs-prune-rate curve — one matrix, two ways to cut it
- Score: 9/10

## Candidate 19 — Where Quantization Hurts
- Source: `embedded-ai/chapters/12-chapter-model-optimization.md`
- Production mode: Manim visualization
- Hook: Shrinking every number from 32 bits to 8 is nearly free — until one tensor quietly loses everything it knew.
- Core idea: int8 maps a float range onto 256 bins, and when a tensor's information lives in tiny magnitudes, many distinct values collapse into the same bin — per-channel scales and quantization-aware training exist to protect exactly those tensors.
- Visual object: A number line of float values snapping into integer bins — the wide-range case surviving, the narrow-range case collapsing
- Manim move: collapse
- Short-form fit: Medium
- Prerequisites: floating point vs integer (cartoon level)
- Exclusions: no scale/zero-point formulas, no symmetric-vs-asymmetric detail, no PTQ-vs-QAT workflow — two number lines, one casualty
- Score: 7/10

## Candidate 20 — The Teacher's Wrong Answers Are the Lesson
- Source: `embedded-ai/chapters/12-chapter-model-optimization.md`
- Production mode: Mixed
- Hook: To train a small network, the ground-truth labels are less useful than a big network's mistakes.
- Core idea: A teacher's soft output — 85% cat, 5% dog — encodes which classes resemble each other, information a one-hot label throws away; a student trained to match that distribution gains accuracy it could never reach from the labels alone.
- Visual object: One image feeding a big teacher and a small student — a flat one-hot bar beside the teacher's rich probability distribution flowing into the student
- Manim move: compare
- Short-form fit: Strong
- Prerequisites: classifier outputs as probabilities
- Exclusions: no temperature/loss equations, no prune-distill-quantize ordering, no KL divergence — the two label pictures carry it
- Score: 8/10

## Candidate 21 — "Conversion Successful" Is Not a Promise
- Source: `embedded-ai/chapters/13-chapter-tinyml-toolchains.md`
- Production mode: Mixed
- Hook: The toolchain printed success at every step — and the deployed model's predictions were garbage.
- Core idea: Deployment pipelines fail silently, so the only truth test is running the same inputs through the source model, the converted model, and the device, and bisecting whichever gap appears first — training frameworks crash loudly, toolchains lie quietly.
- Visual object: A six-gate pipeline glowing all green while an accuracy number degrades across three checkpoints, brackets localizing the drop
- Manim move: trace
- Short-form fit: Medium
- Prerequisites: what model conversion is (loosely)
- Exclusions: no converter code, no calibration-set mechanics, no vendor-compiler tour — green gates, falling number, bisection brackets
- Score: 7/10

## Candidate 22 — The Architecture Physics Chose
- Source: `embedded-ai/chapters/14-chapter-integration-case-studies.md`
- Production mode: Manim visualization
- Hook: The team didn't choose on-device AI — the radio's arithmetic left them nothing else to choose.
- Core idea: One 20 KB image against LoRaWAN's ~30-seconds-per-hour airtime cap means minutes of transmission per picture, so the classifier must run on the sensor and send ten bytes — find the binding constraint early and it designs the system for you.
- Visual object: A payload bar crawling through a narrow bandwidth pipe against an airtime ceiling, then a ten-byte result zipping through
- Manim move: compare
- Short-form fit: Strong
- Prerequisites: bandwidth, what a payload is
- Exclusions: no three-case-study tour, no solar-budget arithmetic, no duty-cycle regulation detail — one image, one pipe, one inescapable conclusion
- Score: 8/10
