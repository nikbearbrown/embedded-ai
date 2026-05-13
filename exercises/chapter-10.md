## LLM Exercise — Chapter 10: Real-Time AI

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** A real-time verdict module that classifies an application's deadline class (soft / firm / hard), checks WCET against the deadline, and recommends a design pattern when AI is in a safety-critical loop.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/realtime.py to the tinyml-feasibility toolkit.

Frozen RealTimeVerdict dataclass:
- real_time_class: Literal["soft", "firm", "hard"]
- predicted_wcet_ms: float (95th-percentile latency × 1.5 safety factor for hard real-time)
- deadline_ms: float
- headroom_pct: float
- safety_class: Literal["non-critical", "iec61508_sil1", "iec61508_sil4", "iso26262_asilA", "iso26262_asilD", "iec62304_classB", "iec62304_classC", "do178c_levelA"]
- design_pattern: Literal["advisory", "bounded_inference", "confidence_gating", "voting", "hierarchical_fallback", "exclude_ai"]
- justification: str
- verdict: Literal["FITS", "TIGHT", "FAILS", "REQUIRES_PATTERN_CHANGE"]
- mitigations: list[str]
- to_markdown() emits a Real-Time section matching Chapter 14's shape

Public functions:
- `assess_realtime(model: ModelSummary, target: Target, app: Application, latency_estimate: LatencyEstimate) -> RealTimeVerdict`
- `recommend_design_pattern(safety_class: str, headroom_pct: float, real_time_class: str) -> str` — returns a pattern name with rationale

Implementation:
- predicted_wcet_ms = latency_estimate.total_ms × 1.5 (conservative — real WCET requires measurement on target)
- For hard real-time AND safety_class in (iso26262_asilD, do178c_levelA): if AI cannot prove WCET deterministically, design_pattern = "exclude_ai" with justification
- For hard real-time + lower safety class: design_pattern = "hierarchical_fallback" — AI advisory, deterministic fallback enforces safety
- For firm real-time: design_pattern = "confidence_gating" — discard low-confidence predictions
- For soft real-time: design_pattern = "advisory" — AI suggests, human or downstream system decides
- Add app fields if missing: safety_class (str)

CLI:
- `tinyml-feasibility check-realtime --app <yaml> --target <name> --model <path>` prints RealTimeVerdict

Tests:
- test_soft_real_time_advisory — soft class, expect "advisory" pattern
- test_hard_asild_excludes_ai — hard real-time + ASIL-D, expect "exclude_ai"
- test_firm_with_low_headroom_gates — firm class + headroom < 20%, expect "confidence_gating"
- test_hard_with_fallback — hard real-time + non-ASIL-D safety, expect "hierarchical_fallback"
```

---

**What this produces:** A real-time verdict that names the safety class, recommends a design pattern from chapter 10's repertoire, and flags when AI must be excluded from the safety-critical path.

**How to adapt this prompt:**
- *For your own project:* The safety_class field needs honest input — it determines everything. Misclassify your application as `non-critical` when it's actually ASIL-B and the toolkit will hand you a deployment that won't certify.
- *For ChatGPT / Gemini:* Works as-is.
- *For Claude Code:* Best fit. The pattern selection is rule-based, easy to test.
- *For a Claude Project:* Pin the safety-class table to the system prompt; it gets read by chapter 14's report generator.

**Connection to previous chapters:** Reads LatencyEstimate (4), Application (1, with safety_class). Produces the design-pattern recommendation that chapter 14's report will surface.

**Preview of next chapter:** Chapter 11 adds `compare.py` — multi-model Pareto comparison. Given N candidate models, rank them by feasibility-margin and accuracy and identify the Pareto frontier.
