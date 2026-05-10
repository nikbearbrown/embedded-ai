## 🛠️ LLM Exercise — Chapter 3: ML for Embedded Engineers

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** A model-loader module that ingests a TFLite (and optionally ONNX) model file and returns the three numbers every downstream module needs: parameter count, MAC count, and largest activation tensor size.
**Tool:** Claude Code

---

**The Prompt:**

```
Extend tinyml-feasibility with a model-loading module.

Add src/tinyml_feasibility/model.py:

Frozen ModelSummary dataclass with fields:
- path: pathlib.Path
- format: Literal["tflite", "onnx", "h5"]
- parameter_count: int
- mac_count: int
- precision: Literal["int8", "int16", "float16", "float32"]
- largest_activation_elements: int  (largest single-tensor activation)
- layer_summary: list[tuple[str, dict]]  (layer name → key parameters)

Public functions:
- `load_model(path: Path) -> ModelSummary` — dispatches on file extension. Implement TFLite first using the `tflite-micro` reference parser or the `tflite` python package.
- `parameter_count(model) -> int` — sum of weight tensor element counts.
- `mac_count(model) -> int` — multiply-accumulate operations per inference (count from layer types: Conv2D, DepthwiseConv2D, FullyConnected dominate; Add, ReLU, Reshape are free).
- `largest_activation(model) -> int` — peak activation tensor element count, which approximates the SRAM ceiling.

CLI extension:
- `tinyml-feasibility inspect-model <path-to-model>` prints ModelSummary fields

Tests:
- test_load_tflite — loads a small TFLite (download a public MobileNetV2-0.35 or use a stub fixture), returns parameter_count > 0
- test_mac_count_conv2d — feeds a single-Conv2D model with known weights, checks MAC count matches the analytical answer (input H × W × in_channels × out_channels × kernel_H × kernel_W)
- test_largest_activation — for a model with known layer sizes, the function returns the maximum

Use `tflite` package (PyPI) or write a minimal FlatBuffers parser. Document which approach in module docstring.
```

---

**What this produces:** `tinyml-feasibility inspect-model my_model.tflite` returns parameter count, MAC count, precision, and largest activation — the three numbers chapters 5–7 will consume to compute memory, compute, and power verdicts.

**How to adapt this prompt:**
- *For your own project:* Drop your `.tflite` file in the package's `examples/` folder and run `inspect-model` to get the three numbers in the format the downstream pipeline expects.
- *For ChatGPT / Gemini:* Works as-is, but ChatGPT may need explicit instruction to use the `tflite` PyPI package rather than reinventing FlatBuffers parsing.
- *For Claude Code:* Best fit. Pip install `tflite`, run pytest, iterate.
- *For a Claude Project:* Add the ModelSummary dataclass to the system prompt — chapters 5–14 will all reference it.

**Connection to previous chapters:** This module produces the structured input that chapters 5 (memory), 6 (compute), 7 (power), and 11 (model selection) will all consume. The Constraint list from chapter 2 is the budget side; ModelSummary is the demand side.

**Preview of next chapter:** Chapter 4 adds `profiling.py` — a latency predictor that takes a ModelSummary and a Target and predicts inference latency stage by stage, using processor-class throughput tables.
