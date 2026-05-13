# Chapter 5 — Memory

The datasheet says 256 KB of RAM. Your model's weights occupy 180 KB. Simple arithmetic: 256 − 180 = 76 KB of headroom. The model fits. You compile, flash, run — and the system crashes 40 ms into the first inference with a memory fault. The debugger shows the heap allocator failed, *malloc* returned null, and the inference engine tried to write to address 0x00000000.

The weights were never the problem. Weights live in flash. What crashed was *activation memory* — the intermediate tensors created during inference, which live in RAM. The model's activation footprint is 210 KB. Add 30 KB for the Bluetooth stack, 8 KB for the system heap, 4 KB for the call stack, and you needed 252 KB of SRAM before inference even started. The model that "fit" by parameter count did not fit at runtime.

This is the failure mode this chapter is built around, because it is invisible until you measure it. Datasheets quote total RAM. Model summaries quote parameter count and weight size. Neither tells you how much RAM inference will consume *while executing*. That number is the hidden constraint, and it is the one that decides whether deployment works.

The first thing to get straight is *which kind of memory which thing lives in*. Embedded memory is not one resource. Flash is non-volatile, abundant (typically 512 KB to 2 MB on a microcontroller), and read-only at runtime. You can write to it, but only through erase-and-program cycles that take milliseconds and wear the part out (10,000 to 100,000 erase cycles, after which the cell stops holding data reliably). Flash holds the firmware binary, the model's weights and biases, and any constant tables — quantization parameters, activation lookup tables, things that never change after deployment. SRAM is volatile, fast (1–2 cycle access), writable, and scarce — typically 64 KB to 512 KB on most parts, with high-end pieces topping out around 1–2 MB. SRAM holds the application heap and stack, global and static variables, RTOS task control blocks, and — the part that matters here — the model's activation tensors during inference, plus any scratch buffers the operations need.

The memory question is therefore not *does the model fit in total memory* but *does each component fit in the right kind of memory*. A model with 500,000 parameters as int8 (500 KB of weights) deployed on an STM32L4 with 640 KB of SRAM and 2 MB of flash has its weights comfortably in flash. If activations require 400 KB of SRAM and the application is already using 200 KB for the BLE stack and buffers, you are sitting at 600 KB of SRAM in use, with 40 KB of margin — which evaporates the moment a 64 KB DMA buffer for sensor data also needs to fit. The deployment fails on SRAM headroom.

Some parts support *execute-in-place* from flash, where the processor fetches instructions and reads constant data directly from flash without copying to SRAM. That works for weights — the inference engine reads from flash on demand. It does not work for activations, because activations change during inference and flash is read-only. Activations need writable memory, which is SRAM or external memory. External memory — PSRAM, SDRAM, eMMC — gets you more capacity, but each access costs 10× to 50× more cycles than on-chip SRAM, more energy per access, and more BOM cost. If you have to put activations there, you are buying capacity in exchange for both latency and power.

Weight memory is the easy half of the problem because it is straightforward to calculate. Count parameters, multiply by bytes per parameter. For a fully connected layer with *I* inputs and *O* outputs, parameters are *(I × O) + O* — the second term is the bias vector. For a 2D convolution with *C_in* input channels, *C_out* output channels, and a *K_h × K_w* kernel, parameters are *(K_h × K_w × C_in × C_out) + C_out*. For depthwise separable convolution, you split it: depthwise is *(K_h × K_w × C) + C*, pointwise is *(C × C_out) + C_out*, total is the sum. Most frameworks report total parameter count when you compile — TensorFlow's `model.summary()`, PyTorch's `torchinfo.summary()`. Multiply by bytes per parameter: 4 for float32, 2 for float16, 1 for int8. A 1 M parameter model is 4 MB as float32, 2 MB as float16, 1 MB as int8. Quantizing to int8 cuts weight memory by 75%, which is what gets a 1.2 MB float32 model fitting on a 1 MB-flash part with firmware overhead.

Some inference engines copy weights from flash into SRAM for faster access. TFLite Micro can be configured to do this. The trade is faster inference (SRAM access beats flash access) for SRAM consumed. If your SRAM budget is tight, leave the weights in flash and accept the latency hit.

Activation memory is the hard half. You cannot calculate it from a parameter count — you have to trace dataflow through the network and account for every intermediate tensor that has to coexist. Take a small CNN: 96 × 96 × 3 input (110 KB as float32), Conv1 producing a 96 × 96 × 32 tensor (1.15 MB), Pool1 reducing to 48 × 48 × 32 (288 KB), Conv2 to 48 × 48 × 64 (576 KB), Pool2 to 24 × 24 × 64 (144 KB), Flatten + FC down to a 10-element output (40 bytes). If you naively allocate a separate buffer per layer, peak memory is the sum: 2.27 MB. That is dead on a 256 KB part.

But you do not have to keep them all alive. Once Conv1's output has been consumed by Pool1, Conv1's buffer can be reused for Conv2's input. This is *buffer reuse*. With it, peak memory becomes the size of the largest tensor that has to exist at any one moment — for this network, Conv1's 1.15 MB output. The peak drops from 2.27 MB to 1.15 MB. Still too big. Drop the input resolution to 48 × 48 and Conv1's output becomes 288 KB as float32, 72 KB as int8. Now it fits.

The activation memory requirement is the maximum of the largest intermediate tensor, the number of tensors that have to coexist (which depends on the dataflow — feedforward networks reuse buffers efficiently; networks with skip connections like ResNet have to hold the skipped tensor live longer), and any scratch buffers specific operations need. The third one is the silent killer. Convolution implementations often use an *im2col* transformation that rearranges the input into a temporary matrix so the convolution becomes a matrix multiply, which is faster on processors that have good matmul kernels. The scratch buffer required is roughly *(output H × output W × kernel H × kernel W × input channels)* — for the same 96 × 96 × 32 input with 3 × 3 kernel, that is 96 × 96 × 9 × 32 ≈ 2.65 M elements, or about 10 MB as float32. Impractical on embedded hardware. Embedded-optimized engines either avoid im2col entirely, doing direct convolution with register blocking, or do partial im2col on tiles small enough to fit in cache so the scratch buffer stays small. CMSIS-NN and TFLite Micro's optimized kernels do the latter.

Three layout strategies reduce activation memory. *In-place computation* writes a layer's output to the same buffer that held its input — possible for element-wise operations like ReLU, batch normalization, residual addition, where output dimensions match input. The engine reads `input[i]`, computes the result, writes back to `input[i]`. No additional buffer. ReLU activation memory is zero. *Buffer reuse* recycles buffers across layers as just described. *Scratch pads* are temporary buffers for operations that need intermediate storage, and the engine's job is to keep them small.

You control all of this by configuring the inference engine at compile time. TFLite Micro requires a static *tensor arena*:

```c
constexpr int kTensorArenaSize = 200 * 1024; // 200 KB
alignas(16) uint8_t tensor_arena[kTensorArenaSize];

tflite::MicroInterpreter interpreter(model, resolver, tensor_arena, kTensorArenaSize);
```

If the arena is too small, initialization fails with a message that tells you the required size. You bump it, recompile, retest. If the arena fits but the system crashes later, the arena plus the rest of the firmware (heap, stack, BLE buffers, sensor DMA, RTOS structures) exceeded total SRAM. The workflow is: start with the smallest arena initialization will accept, add 20% margin for runtime variation, verify total SRAM usage stays below 80% of capacity (you need headroom for interrupt stack growth, communication buffers filling under load, and other runtime variation), and if it does not, shrink the model or add external memory.

Dynamic allocation during inference is a design error on embedded systems. The heap is unreliable, fragmentation is unavoidable, and allocation failures are unrecoverable. The correct pattern is *static pre-allocation*: the tensor arena is a static array allocated at compile time; weights are either in flash (read-only) or copied once to a static SRAM array during initialization; input and output buffers are static; scratch buffers, where needed, are static. Nothing is allocated with `malloc` or `new` during inference. The advantage is predictability — you know at compile time whether the model fits, you know inference cannot fail from heap exhaustion, you know memory usage is constant across inference passes. The disadvantage is rigidity — switching to a different model means recompiling. For most embedded AI applications, the trade is correct: you deploy one model that runs on fixed hardware for months or years, and you want it deterministic. TFLite Micro enforces static allocation by default; PyTorch Mobile and ONNX Runtime assume dynamic allocation and have to be configured explicitly to use pre-allocated buffers. Verify, do not assume.

Profiling is how you bridge theoretical and actual. The simplest method is to fill unused RAM with a known pattern, run inference, and count how many bytes were overwritten:

```c
extern uint8_t _end; // end of .bss section (linker-provided)
extern uint8_t _estack; // top of stack
memset(&_end, 0xAA, &_estack - &_end);

run_inference();

uint8_t *ptr = &_end;
size_t used = 0;
while (ptr < &_estack && *ptr != 0xAA) { ptr++; used++; }
printf("RAM used: %zu bytes\n", used);
```

That counts everything — stack growth, heap, the lot. For finer granularity, the framework's profiler tells you how much of the tensor arena was actually used (TFLite Micro: `interpreter.arena_used_bytes()`); you can sometimes get layer-by-layer memory traces; and external tools — Percepio Tracealyzer, SEGGER SystemView, ARM's profiler — visualize memory usage in real time on RTOS-based systems. The questions to answer are: peak SRAM usage, which layer or operation drove the peak, and whether headroom is left for the rest of the system. If peak usage exceeds 80% of total SRAM, you are in the danger zone, because real systems have runtime variation that controlled testing does not catch.

To make this concrete, work an actual deployment. MobileNetV2-based image classifier on an STM32H743 (Cortex-M7 at 480 MHz, 1 MB SRAM, 2 MB flash). Model: 1.2 M parameters int8-quantized, 1.2 MB in flash. The summary reports a 96 × 96 × 3 input and the largest layer output as 24 × 24 × 192 (110,592 elements, 108 KB at int8). Conservative estimate with 50% margin for scratch: 162 KB. Allocate a 200 KB arena, deploy.

Initialization succeeds. First inference crashes with a memory fault. Check actual usage. The interpreter reports it needed 340 KB, not 162 KB. Why? Because the bottleneck was not the 24 × 24 × 192 tensor — it was a depthwise convolution's im2col scratch buffer at 180 KB, which the conservative estimate did not account for. *Operation-specific scratch memory is the thing that surprises you.*

Bump the arena to 350 KB. Initialization succeeds. Inference runs and then crashes 80 ms in with a stack overflow. Check total SRAM: arena 350 KB, application heap 80 KB, RTOS kernel and task stacks 120 KB, communication buffers 200 KB, globals 50 KB. That is 800 KB used, leaving 224 KB of the 1 MB part for the call stack — and the inference function's deeply-nested layer dispatching overflows it.

Cannot increase SRAM, the hardware is fixed. Reduce the model. Drop input resolution from 96 × 96 to 80 × 80. Drop maximum channel count from 192 to 128. Replace standard convolutions with depthwise separable, which carry smaller scratch buffers. Retrain. The new model has 800 K parameters (800 KB as int8), largest layer output 20 × 20 × 128 = 50 KB, and the tensor arena measures at 180 KB. New SRAM total: arena 180 KB, heap 80 KB, RTOS 120 KB, comms 200 KB, globals 50 KB — 630 KB used, 394 KB of headroom, comfortable. Deploy. It runs. Accuracy went from 89.2% on the original model to 86.4% on the reduced one — a 3% drop, acceptable for the application.

The original "fit" by parameter count: 1.2 MB weights in 2 MB of flash, plenty of room. The actual runtime requirement was 340 KB of activation memory plus all the rest of the firmware, on a part with 1 MB total SRAM. Profiling exposed the scratch-buffer overhead. Shrinking the model brought it back into envelope at a known accuracy cost.

When the memory constraint fails, it fails one of three ways. *Doesn't fit in flash* — quantize float32 to int8 (75% reduction), prune layers, pick a smaller architecture. *Doesn't fit in SRAM* — reduce layer sizes and channel counts, prefer architectures with lower activation memory (MobileNet over ResNet), or add external PSRAM. *Insufficient margin* — the model fits but total SRAM usage is at 90% of capacity, which works in testing and crashes under load. Reduce model footprint, reduce application memory, or upgrade hardware.

Memory is binary. The model fits or it does not. If it does not fit, no amount of compute optimization or power tuning saves you. That is why this chapter comes before all the others in Part II. Before you measure latency, before you measure power, before you reach for accelerators — verify the model fits, with margin. The next chapter takes the second constraint: compute.

---

## LLM Exercise — Chapter 5: Memory

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** The first verdict module — `memory.py` — which compares a model's flash + SRAM demands against a target's budget and emits a typed verdict with mitigations.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/memory.py to the tinyml-feasibility toolkit.

Frozen MemoryVerdict dataclass:
- weight_kb: float
- activation_kb: float
- scratch_kb: float
- total_sram_kb: float
- flash_margin_pct: float
- sram_margin_pct: float
- verdict: Literal["FITS", "TIGHT", "FAILS"]
- mitigations: list[str] (suggestions if TIGHT or FAILS)
- to_markdown() method — emits a section in the same shape as Chapter 14's case-study memory blocks

Public function:
`assess_memory(model: ModelSummary, target: Target, scratch_overhead: float = 0.5) -> MemoryVerdict`

Implementation:
- weight_kb = model.parameter_count * bytes_per_element(model.precision) / 1024
- activation_kb = model.largest_activation_elements * bytes_per_element / 1024
- scratch_kb = activation_kb * scratch_overhead (im2col approximation)
- total_sram_kb = activation_kb + scratch_kb
- flash_margin_pct = (target.flash_kb - weight_kb) / target.flash_kb * 100
- sram_margin_pct = (target.sram_kb - total_sram_kb) / target.sram_kb * 100
- verdict: FITS if both margins > 20; FAILS if either < 0; TIGHT otherwise
- mitigations dict-driven from chapter 5's repertoire:
 - if weight_kb is the bottleneck: "Quantize float32 → int8 (75% weight reduction)", "Switch to smaller MobileNet width multiplier"
 - if activation_kb is the bottleneck: "Buffer reuse (20-40% activation reduction)", "In-place computation", "Smaller input resolution"
 - if scratch_kb is the bottleneck: "Switch to direct convolution kernels (no im2col)"

CLI extension:
- `tinyml-feasibility check-memory --app <yaml> --target <name> --model <path>` prints the MemoryVerdict and includes the to_markdown() output

Tests:
- test_fits_case — large flash + SRAM, expect FITS, mitigations is empty
- test_fails_flash — model 2× target flash, expect FAILS, mitigations names quantization or smaller variant
- test_tight_sram — sram margin = 5%, expect TIGHT, mitigations names buffer reuse
- test_to_markdown_section_shape — output starts with "## Memory" and contains all numeric fields
```

---

**What this produces:** A typed verdict module that, given a model + target, tells you whether the memory budget closes — with named mitigations when it doesn't and a Markdown emitter that's already shaped to drop into the integration report you'll generate in chapter 14.

**How to adapt this prompt:**
- *For your own project:* Tune `scratch_overhead` based on your model architecture — pure depthwise-separable models need less scratch; standard convolutions need more.
- *For ChatGPT / Gemini:* Works as-is.
- *For Claude Code:* Best fit. Run pytest after each iteration.
- *For a Claude Project:* The MemoryVerdict dataclass and verdict thresholds become reusable in chapters 6, 7, 11, and 14.

**Connection to previous chapters:** Reads ModelSummary (chapter 3) and Target (chapter 2). Produces the first FITS/TIGHT/FAILS verdict — the verdict pattern repeats in chapters 6, 7, 8, 9, 10, and gets aggregated in chapter 14.

**Preview of next chapter:** Chapter 6 adds `compute.py` — same verdict pattern, this time comparing predicted latency (chapter 4) against the latency constraint, with processor-class upgrade recommendations as mitigations.

---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **An Wang** invented magnetic core memory — the technology that stored every bit in every computer for two decades, the spiritual ancestor of the SRAM you're allocating tensors into now.

**Run this:**

```
Who was An Wang, and how does his work on magnetic core memory connect to the SRAM and flash trade-offs in modern embedded AI systems? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"An Wang"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain how magnetic core memory worked, in plain language
- Ask it to compare core memory's energy and access cost to today's SRAM, in numbers
- Add a constraint: "Answer as if you're explaining it to an embedded engineer who has only ever used flash and SRAM"

What changes? What gets better? What gets worse?
