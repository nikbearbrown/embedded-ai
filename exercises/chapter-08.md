## 🛠️ LLM Exercise — Chapter 8: Hardware for AI

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** An accelerator decision module — given a model and a target without an NPU, evaluate whether moving to an accelerator-equipped target closes the budget and at what cost.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/accelerator.py to the tinyml-feasibility toolkit.

Frozen AcceleratorDecision dataclass:
- baseline_target: Target  (current pick, CPU-only)
- baseline_verdict: dict  (combined memory+compute+power verdict from prior modules)
- candidate_targets: list[Target]  (TARGETS where has_accelerator=True)
- candidate_verdicts: list[dict]
- recommendation: Literal["KEEP_BASELINE", "UPGRADE_TO_NPU", "INSUFFICIENT_DATA"]
- recommended_target: Target | None
- justification: str  (one paragraph naming the constraint that decided)
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
