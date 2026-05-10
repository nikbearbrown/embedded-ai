## 🛠️ LLM Exercise — Chapter 13: TinyML Toolchains and Deployment Pipelines

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** A deployment runner — a TFLite-converter wrapper that runs the conversion, simulates on-target inference via the TFLite Python interpreter, and emits a verification report comparing simulated outputs against the original training-model outputs.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/deploy.py to the tinyml-feasibility toolkit.

Frozen DeploymentReport dataclass:
- source_model_path: Path
- converted_model_path: Path
- conversion_succeeded: bool
- conversion_warnings: list[str]
- calibration_set_size: int
- mean_absolute_error_vs_source: float  (across the validation samples)
- max_absolute_error_vs_source: float
- accuracy_drift_pct: float  (deployed accuracy − source accuracy, negative if drift down)
- toolchain_loss_flagged: bool  (True if drift > 2 percentage points — bisection signal)
- ops_used: list[str]  (every op from the converted model that needs to be in the OpResolver)
- estimated_tensor_arena_kb: int
- to_markdown() emits a Deployment section matching Chapter 14's shape

Public functions:
- `convert_to_tflite(source_path: Path, calibration_data: list, optimization: str = "default", output_path: Path | None = None) -> Path`
- `verify_against_source(source_path: Path, converted_path: Path, validation_samples: list) -> DeploymentReport`
- `extract_ops_required(tflite_path: Path) -> list[str]` — returns the op names needed in the OpResolver (Conv2D, DepthwiseConv2D, Fully Connected, Softmax, etc.)

Implementation:
- Use tensorflow's TFLiteConverter for the conversion path; run with int8 PTQ as default.
- Verification compares source-model softmax outputs against converted-model softmax outputs on the same inputs. NEVER fabricate validation accuracy — require the user to pass real validation samples.
- Toolchain-loss flag: if accuracy_drift > 2pp, recommend bisection (disable layer fusion, swap calibration set, check op mappings).
- estimated_tensor_arena_kb comes from running interpreter.allocate_tensors() and reading the arena size.

CLI:
- `tinyml-feasibility deploy --source <path-to-source-model> --calibration <path-to-calibration-yaml> --validation <path-to-validation-yaml>` runs the full conversion + verification and prints DeploymentReport

Tests:
- test_conversion_succeeds — feed a simple Keras model, expect conversion_succeeded=True
- test_verification_low_drift — feed matched inputs, expect mean_absolute_error < 0.01
- test_toolchain_loss_flagged — synthesize a case where converter introduces 5pp drift, expect toolchain_loss_flagged=True with bisection suggestions

Note: this module requires `tensorflow` as an optional dependency. Document the install path in README.
```

---

**What this produces:** A single command that does what chapter 13 narrates — converts the model, runs verification, and tells you whether the conversion lied. If the converter "succeeded" but the deployed model drifts >2pp from the source, the report flags it and recommends bisection.

**How to adapt this prompt:**
- *For your own project:* The validation samples are critical. Use 50-200 samples drawn from your actual deployment distribution, not training data.
- *For ChatGPT / Gemini:* Works as-is, though tensorflow setup is finicky in browser-based environments — Claude Code is the right tool for the conversion run.
- *For Claude Code:* Best fit. Use `--allowed-tools edit,bash,web_search` so it can install tensorflow and execute the conversion.
- *For a Claude Project:* Add the calibration-set quality checklist to the system prompt — it's the most common silent-failure source.

**Connection to previous chapters:** Reads the OptimizationPlan (12) to know what conversions to run. Outputs feed the integration report in chapter 14.

**Preview of next chapter:** Chapter 14 adds `report.py` — the integration-decision-document generator that aggregates every prior verdict into a single Markdown decision doc matching the shape of Chapter 14's three case studies. Plus integration tests that replicate those three case studies as `tinyml-feasibility report` invocations.
