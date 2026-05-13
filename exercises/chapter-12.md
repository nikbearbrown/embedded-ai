## LLM Exercise — Chapter 12: Optimizing Models — Quantization, Pruning, Distillation

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
- justification: str (why this step was inserted at this position)

Frozen OptimizationPlan dataclass:
- baseline_model: ModelSummary
- baseline_accuracy_pct: float
- target_constraints: dict (the four-constraint targets)
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
