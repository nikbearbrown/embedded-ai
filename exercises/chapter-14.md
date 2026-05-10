## 🛠️ LLM Exercise — Chapter 14: Integration Case Studies — Full Design Decisions

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** The integration-report generator that aggregates every prior verdict into a single Markdown decision document matching the shape of Chapter 14's three case studies — plus integration tests that replicate those case studies as toolkit invocations.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/report.py to the tinyml-feasibility toolkit. This is the capstone module.

Frozen IntegrationReport dataclass:
- application: Application
- target: Target
- model: ModelSummary
- memory_verdict: MemoryVerdict
- compute_verdict: ComputeVerdict
- power_verdict: PowerVerdict
- accelerator_decision: AcceleratorDecision
- comms_recommendation: TierRecommendation
- realtime_verdict: RealTimeVerdict
- model_selection: ParetoFrontier | None
- optimization_plan: OptimizationPlan | None
- deployment_report: DeploymentReport | None
- binding_constraint: Literal["memory", "compute", "power", "real_time", "comms_bandwidth", "regulation", "accuracy"]
- rejected_alternatives: list[dict]  (each: name, reason, citation back to verdict)
- risk_register: list[str]
- to_markdown() emits the full decision document — same structure as Chapter 14's three case studies

Public functions:
- `generate_report(application: Application, target: Target, model: ModelSummary, **optional_modules) -> IntegrationReport`
- `identify_binding_constraint(report: IntegrationReport) -> str` — pick the axis with smallest headroom or first FAILS verdict
- `extract_rejected_alternatives(report) -> list[dict]` — pull every TIER, target, or model that was considered and rejected, with citations

Implementation:
- generate_report runs every prior module in order, collects verdicts, identifies the binding constraint, populates the rejection log.
- to_markdown produces 9 numbered sections matching Chapter 14's case studies: Application & stakes, Constraints, Model selection, Hardware, Optimization, Deployment, Validation, Risks & rejected alternatives, Closing (what would change my mind / still puzzling).

CLI:
- `tinyml-feasibility report --app <yaml> --target <name> --model <path> --output <output.md>` runs the full chain and writes the Markdown report.

Integration tests in tests/test_integration.py:
- test_industrial_vibration_case — given the YAML for the industrial vibration case (200 CNC machines, 18-month battery, $40 BOM), the toolkit recommends the random forest on STM32L4R5, identifies "power" as binding, lists the rejected 1D CNN with reason
- test_medical_wearable_case — given the ECG wearable YAML, the toolkit recommends 1D CNN on STM32U5 with prune-distill-QAT optimization plan, identifies "accuracy/regulation" as binding
- test_agricultural_sensor_case — given the vineyard YAML, the toolkit recommends EfficientNet-Lite0 on RPi-Zero-2W, identifies "comms_bandwidth" as binding (LoRaWAN cannot move images)

Each integration test pins the recommendation against the case study's narrative — the toolkit must reproduce those three architecture verdicts. If it doesn't, the rule encoding is wrong somewhere upstream.

These three integration tests double as the regression suite. The toolkit ships when all three pass.

Run pytest. All unit tests + all three integration tests pass before you stop.
```

---

**What this produces:** A working open-source toolkit that takes a YAML application spec, a target chip, and a TFLite model and emits a full deployment-decision document — the same shape as Chapter 14's case studies. The three integration tests demonstrate that the toolkit reproduces those case studies' architecture verdicts directly. Ships as a pip-installable package an embedded engineer can drop into a CI pipeline.

**How to adapt this prompt:**
- *For your own project:* Run `tinyml-feasibility report --app your_app.yaml --target your_target --model your_model.tflite --output decision.md` and you have the design-review document. Edit prose; toolkit produced the math.
- *For ChatGPT / Gemini:* Works as-is.
- *For Claude Code:* Best fit. Use `--allowed-tools edit,bash` to run the integration test suite.
- *For a Claude Project:* The full toolkit becomes a system-prompt artifact — drop the package in and ask Claude to evaluate new applications.

**Connection to previous chapters:** This module aggregates outputs from chapters 1 (Application), 2 (Target, Constraints), 3 (ModelSummary), 4 (LatencyEstimate), 5 (MemoryVerdict), 6 (ComputeVerdict), 7 (PowerVerdict), 8 (AcceleratorDecision), 9 (TierRecommendation), 10 (RealTimeVerdict), 11 (ParetoFrontier), 12 (OptimizationPlan), 13 (DeploymentReport). The integration tests demonstrate that the framework, encoded as code, produces the same architectural answers that Chapter 14's prose narrates.

**Preview of next chapter:** None — this is the capstone. Use the toolkit on a real application of your choosing as your final project.
