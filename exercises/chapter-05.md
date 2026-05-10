## 🛠️ LLM Exercise — Chapter 5: Memory

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
- mitigations: list[str]  (suggestions if TIGHT or FAILS)
- to_markdown() method — emits a section in the same shape as Chapter 14's case-study memory blocks

Public function:
`assess_memory(model: ModelSummary, target: Target, scratch_overhead: float = 0.5) -> MemoryVerdict`

Implementation:
- weight_kb = model.parameter_count * bytes_per_element(model.precision) / 1024
- activation_kb = model.largest_activation_elements * bytes_per_element / 1024
- scratch_kb = activation_kb * scratch_overhead  (im2col approximation)
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
