## 🛠️ LLM Exercise — Chapter 4: Inference Mechanics

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** A latency predictor that decomposes a model's inference into the four pipeline stages and estimates each stage's wall-clock time on a given target.
**Tool:** Claude Code

---

**The Prompt:**

```
Extend tinyml-feasibility with a latency-prediction module grounded in the four-stage pipeline (acquire, preprocess, run, postprocess).

Add src/tinyml_feasibility/profiling.py:

Frozen LatencyEstimate dataclass:
- acquire_ms: float  (sensor read time; default 1.0, override by app config)
- preprocess_ms: float  (e.g., MFCC for audio, normalization for vision)
- inference_ms: float
- postprocess_ms: float
- total_ms: float
- bottleneck_stage: Literal["acquire", "preprocess", "run", "postprocess"]
- assumption_notes: list[str]  (every estimate that came from a lookup table goes here)

Public functions:
- `predict_inference_ms(model: ModelSummary, target: Target) -> float` — uses MAC throughput lookup. Provide a CORE_THROUGHPUT dict mapping core string ("Cortex-M0+", "Cortex-M4", "Cortex-M7", "Cortex-M55", "Cortex-A53") to MAC/sec at 1 MHz with int8 + CMSIS-NN. Source each value with a citation comment (e.g., ARM benchmark URLs, CMSIS-NN README).
- `predict_pipeline(model, target, app) -> LatencyEstimate` — returns full breakdown.

CLI extension:
- `tinyml-feasibility predict-latency --app <yaml> --target <name> --model <path>` prints the LatencyEstimate with bottleneck_stage flagged.

Tests:
- test_predict_inference_scales_with_clock — same model on Cortex-M4 at 64 MHz vs 128 MHz: latency at 128 MHz is approximately half (within 10%)
- test_predict_inference_scales_with_macs — doubling MAC count approximately doubles inference latency
- test_pipeline_bottleneck_correctness — for a synthetic case where preprocess dominates, bottleneck_stage == "preprocess"

Note: the lookup tables are imperfect approximations. Document this clearly in the module docstring — the tool predicts within roughly 2x of measured latency on real hardware. Real profiling on target is still required before committing to a deployment.
```

---

**What this produces:** `tinyml-feasibility predict-latency --app jaguar.yaml --target STM32L4R5 --model jaguar_dscnn.tflite` returns a four-stage latency breakdown with the bottleneck stage flagged and explicit assumption notes.

**How to adapt this prompt:**
- *For your own project:* Override the default `acquire_ms` and `preprocess_ms` in your application YAML if your sensor or preprocessing pipeline is non-standard.
- *For ChatGPT / Gemini:* Works as-is. Both will fabricate throughput numbers if not pinned to citations — be aggressive in the prompt about NO FABRICATION and require URLs in comments.
- *For Claude Code:* Use `--allowed-tools edit,bash,web_search`; it will look up CMSIS-NN benchmarks for the throughput table.
- *For a Claude Project:* Add the CORE_THROUGHPUT dict to a shared file in the project so chapters 6 and 8 can extend it.

**Connection to previous chapters:** Consumes the ModelSummary (chapter 3) and Target (chapter 2). Produces the latency input that chapter 6 will compare against the latency budget.

**Preview of next chapter:** Chapter 5 adds the first verdict module — `memory.py` — which compares a model's flash + SRAM demands against a target's budget and emits a FITS / TIGHT / FAILS verdict with named mitigations.
