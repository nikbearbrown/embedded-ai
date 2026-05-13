## LLM Exercise — Chapter 6: Compute

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** The compute verdict module — same pattern as memory, but comparing predicted latency against the latency constraint and emitting processor-class upgrade recommendations when the budget doesn't close.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/compute.py to the tinyml-feasibility toolkit.

Frozen ComputeVerdict dataclass:
- predicted_latency_ms: float
- latency_budget_ms: float
- headroom_pct: float
- arithmetic_intensity: float (MACs per byte of activation traffic — flags memory-bound vs compute-bound)
- verdict: Literal["FITS", "TIGHT", "FAILS"]
- mitigations: list[str]
- upgrade_path: list[Target] (targets in TARGETS that would close the budget, ranked by cost)
- to_markdown() method emits a Compute section matching Chapter 14's shape

Public function:
`assess_compute(model: ModelSummary, target: Target, app: Application) -> ComputeVerdict`

Implementation:
- predicted_latency_ms comes from profiling.predict_pipeline (chapter 4)
- headroom_pct = (latency_budget - predicted) / latency_budget * 100
- arithmetic_intensity = mac_count / (largest_activation_elements * 2) (rough; flags <1.0 as likely memory-bound)
- verdict: FITS if headroom > 20%; FAILS if headroom < 0; TIGHT otherwise
- mitigations from chapter 6's repertoire:
 - if compute-bound: "Boost clock", "Add SIMD-optimized kernel (CMSIS-NN)", "Reduce model MAC count via pruning"
 - if memory-bound: "Reduce activation footprint", "Add data prefetch", "Reduce input resolution"
- upgrade_path: filter TARGETS to those whose predicted latency on this model is < latency_budget; sort by cost_usd ascending, take top 3

CLI:
- `tinyml-feasibility check-compute --app <yaml> --target <name> --model <path>` prints ComputeVerdict and the upgrade_path table

Tests:
- test_fits_fast_processor — STM32H7 + small model, expect FITS
- test_fails_slow_processor — STM32L4R5 + heavy MobileNet, expect FAILS, upgrade_path includes STM32H7
- test_arithmetic_intensity_flag — model with very small activations and many MACs flagged compute-bound
```

---

**What this produces:** `tinyml-feasibility check-compute --app jaguar.yaml --target STM32L4R5 --model jaguar_dscnn.tflite` returns predicted latency, headroom, verdict, and a ranked list of next-tier targets that would close the budget if the current one fails.

**How to adapt this prompt:**
- *For your own project:* The upgrade_path is your shopping list when the first hardware pick fails. Take the cheapest target that fits.
- *For ChatGPT / Gemini:* Works as-is.
- *For Claude Code:* Best fit. The verdict pattern is now established; this chapter reinforces it.
- *For a Claude Project:* Add the verdict-pattern template to the system prompt — chapters 7–10 will reuse the same shape.

**Connection to previous chapters:** Consumes ModelSummary (3), Target (2), Application (1), and `profiling.predict_pipeline` (4). The verdict pattern from chapter 5 now repeats; chapter 14 will aggregate them.

**Preview of next chapter:** Chapter 7 adds `power.py` — energy-balance equation, average power, battery life, and duty-cycle recommendations. Power is the constraint where most embedded AI projects actually break.
