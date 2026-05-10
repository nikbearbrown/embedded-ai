## 🛠️ LLM Exercise — Chapter 11: Selecting Models for Constrained Deployment

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** A multi-model Pareto comparison module — given N candidate models, score each against the application's constraints and identify which lie on the Pareto frontier.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/compare.py to the tinyml-feasibility toolkit.

Frozen ModelCandidate dataclass:
- model: ModelSummary
- accuracy_pct: float  (validation accuracy on the app's dataset; supplied by user)
- memory_verdict: MemoryVerdict
- compute_verdict: ComputeVerdict
- power_verdict: PowerVerdict
- meets_all_constraints: bool

Frozen ParetoFrontier dataclass:
- candidates: list[ModelCandidate]
- pareto_optimal_indices: list[int]  (indices of candidates on the frontier)
- recommended_index: int  (best feasible candidate per the chosen criterion)
- selection_criterion: Literal["max_accuracy_within_constraints", "max_margin_above_threshold", "min_latency"]
- rejection_log: dict  (rejected_model_name → reason string)
- to_markdown() emits a Model Selection section matching Chapter 14's shape, including a Pareto frontier description

Public functions:
- `compare_models(candidates: list[tuple[ModelSummary, float]], target: Target, app: Application) -> ParetoFrontier`
- `pareto_frontier(candidates: list[ModelCandidate]) -> list[int]` — indices of non-dominated candidates on (latency, accuracy)

Implementation:
- For each candidate, run memory + compute + power assessments on the target.
- meets_all_constraints = all three FIT or TIGHT (not FAILS).
- Pareto frontier: candidate i is dominated if some candidate j has both lower latency AND higher accuracy. Keep non-dominated.
- selection_criterion default: "max_accuracy_within_constraints" — pick candidate on the frontier with highest accuracy_pct that meets_all_constraints. If none qualify, return None and populate rejection_log.

CLI:
- `tinyml-feasibility compare-models --app <yaml> --target <name> --models <path1>:<acc1>,<path2>:<acc2>,...` prints the ParetoFrontier including a sortable table

Tests:
- test_pareto_dominance_basic — 5 candidates with known dominance pattern, frontier returns the expected 3
- test_recommended_meets_constraints — recommended candidate's meets_all_constraints is True
- test_rejection_log_explains_failures — for a candidate that fails on memory, rejection_log[name] contains "memory"
```

---

**What this produces:** Replicates chapter 11's fall-detector worked example as a single CLI invocation. Pass 5 candidate models and the toolkit returns the Pareto frontier, the recommended candidate, and the rejection rationale for each that didn't make it.

**How to adapt this prompt:**
- *For your own project:* You provide the accuracy numbers (the toolkit can't measure them — that's your training pipeline's job). The toolkit profiles the rest.
- *For ChatGPT / Gemini:* Works as-is.
- *For Claude Code:* Best fit. Multi-model comparison generates a lot of output; pipe to a CSV or Markdown table.
- *For a Claude Project:* Add the Pareto-frontier algorithm as a reusable utility — chapter 12's optimization planner reuses it.

**Connection to previous chapters:** Aggregates the verdict outputs from chapters 5, 6, 7. Becomes the input that chapter 12's optimization planner uses to identify which candidate is closest to fitting and what compression sequence would close the gap.

**Preview of next chapter:** Chapter 12 adds `optimize.py` — given a model that almost fits, predict the savings from quantization, pruning, and distillation, in the order chapter 12 recommends.
