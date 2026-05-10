# Chapter 3 — Machine Learning for Embedded Engineers

Open a `.tflite` file in a hex editor. You see a binary blob — structured data, not executable code. Somewhere in those bytes are floating-point numbers arranged in matrices, integers describing tensor shapes, and metadata specifying how data flows through a graph of operations. This file is the artifact you will deploy. It was produced by a training process you may never run, on datasets you may never see, on servers with resources your target part cannot imagine. None of that matters once the file exists. What matters is that the file is now a fixed data structure with known size, known operations, and a knowable cost to execute.

The job of this chapter is to give you the literacy to reason about that artifact. Not to train it — that is the machine-learning engineer's job. To *read* it as a design object whose resource demands you can pull out of its specification, the way you pulled hardware constraints out of a datasheet last chapter. This is ML literacy for integration, not for invention. It is enough.

A neural network is a function approximator. You give it inputs; it produces outputs; the relationship between the two is determined by parameters that were learned from data. *Supervised learning* is the most common way to produce those parameters. You collect input-output pairs where the outputs are labeled — images with category labels, audio spectrograms with word labels, sensor readings with normal/fault labels — and a training algorithm adjusts the parameters iteratively to make the model's predictions match the labels. After enough iterations, on inputs the model has not seen before, the predictions are usually right.

Then training stops. The parameters freeze. The model becomes, functionally, a deterministic lookup: given any input from the distribution it was trained on, it produces a prediction by running its inputs through that fixed set of parameters. Those parameters are what you store in flash. Their count and precision determine the model's size on disk. Training happened once, on a GPU server, in hours or days. Inference happens repeatedly, on your part, with the budget Chapter 2 quantified. The literature sometimes blurs the two — *deep learning on microcontrollers* almost always means inference on microcontrollers, because training in 256 KB of RAM is impractical for all but the smallest models. Your problem is inference. Treat training as a black box upstream of you.

Inside the model, the architecture is a directed graph. The most common shape is a *feedforward* network in which data flows through a sequence of layers from input to output. Each layer carries two kinds of data. *Weights* (the learned parameters) are fixed after training. *Activations* (the intermediate results computed at runtime) are not — they are what the layer computes from its input and passes to the next layer. Weights live in flash. Activations live in RAM. The total weight count sets your flash budget. The peak activation size sets your RAM budget. Two different numbers, two different memory regions, both required.

To make this concrete, take a small feedforward network: 784 input neurons (a 28×28 grayscale image flattened), one hidden layer of 128 neurons, an output layer of 10 classes. The hidden layer has a weight matrix connecting every input to every hidden unit: 784 × 128 = 100,352 weights, plus 128 biases. As float32, that is about 401 KB. The output layer is 128 × 10 = 1,280 weights plus 10 biases — about 5 KB. Total weights: ~406 KB, easily inside a 1 MB flash. The activations, by contrast, are tiny: 128 floats out of the hidden layer (512 bytes), 10 floats out of the output (40 bytes). Under 1 KB peak activation memory.

That ratio — weights huge, activations tiny — flips when you scale up. A convolutional network for image classification has dozens of layers and produces large activation tensors at every step. Activation memory can dominate weight memory by an order of magnitude.

Inference itself is a forward pass. You load the input, hand it to the first layer, compute that layer's output, hand the output to the next layer, and repeat. Each layer does two things: a *linear* transformation followed by a *nonlinear* activation function. The linear part is a matrix multiplication for fully connected layers, a convolution for convolutional layers — this is where the weights are used. The nonlinear part is applied element-wise to the output: ReLU (replace negatives with zero), sigmoid, tanh, and a few others. ReLU is cheap — one comparison per element. Sigmoid and tanh involve exponentials, which are noticeably more expensive on processors without hardware support. The choice of activation function matters more in embedded inference than in cloud inference for exactly this reason.

The operation count for a fully connected layer is *(input size) × (output size)* multiply-accumulates. For the small network above, that is about 101,600 MACs total — at 60 MMAC/s sustained, roughly 1.7 ms of inference. At 10 MMAC/s (a slower core, or float emulated on a no-FPU part), about 10 ms. The cost is the operation count multiplied by the time per operation. Architecture sets the first; processor sets the second. Together they set the latency.

Fully connected layers are simple but bad for image data. A 224×224 RGB image is 150,528 pixels; a fully connected layer connecting that to even 128 output neurons would need 19 million weights — 76 MB as float32, which is dead on arrival for most embedded targets. *Convolutional* layers solve this by exploiting spatial locality. Instead of connecting every input to every output, a convolutional layer applies a small filter — say 3×3 — that slides across the image, computing a weighted sum at each position, and reuses the same filter weights across the whole image. Nine weights per filter, times the number of filters, instead of one weight per pixel-output pair. The parameter count drops by orders of magnitude, and the 2D spatial structure of the image is preserved in a way the flat-vector layer cannot.

The operation count for a convolutional layer is *(output H) × (output W) × (output channels) × (kernel H) × (kernel W) × (input channels)*. For a 224×224 RGB input with 32 output channels and a 3×3 kernel, that is 224 × 224 × 32 × 3 × 3 × 3 ≈ 43.6 million MACs. Expensive — but far cheaper than the equivalent fully connected layer, and accurate enough on real images that the family of *convolutional neural networks* (CNNs) has dominated embedded vision for a decade.

A typical CNN stacks several convolutional layers (each extracting features), interleaves them with *pooling* layers that reduce spatial resolution by taking, say, the maximum value in each 2×2 region, and ends with a few fully connected layers that turn the spatial feature maps into class predictions. A well-designed CNN for a 96×96 input can do useful classification with 200,000 to 500,000 parameters and fit in a couple of megabytes of flash when quantized.

The two important efficient-CNN ideas to know by name are *depthwise separable convolution* and the *MobileNet* family that uses it. A standard 3×3 convolution with 32 input channels and 64 output channels does 3 × 3 × 32 × 64 = 18,432 multiplications per output pixel — combining spatial filtering and channel mixing in one operation. Depthwise separable splits that into two cheaper steps: a depthwise convolution that filters each input channel independently (3 × 3 × 32 = 288 mults per output pixel), followed by a 1×1 pointwise convolution that mixes channels (1 × 1 × 32 × 64 = 2,048 mults per output pixel). Total: 2,336, which is roughly an eighth of the standard convolution. Accuracy loss for many vision tasks is small; the cost reduction is large. MobileNetV2 — 3.5 million parameters, ~300 million MACs per inference, ~90% top-5 on ImageNet — is the canonical version. Scaled down to 96×96 input and a 0.35× width multiplier, it drops to ~400,000 parameters and ~25 million MACs, which fits a Cortex-M7 with a couple hundred milliseconds of inference latency. That scaled version is the sweet spot for embedded vision: accurate enough for real tasks, cheap enough to run.

Recurrent networks are the architecture you have to be careful with. *RNNs* are designed for sequence data — time series, audio, text — and they carry a hidden state from one time step to the next, which is what makes them powerful at sequential tasks. The hidden state is also what makes them painful on embedded hardware. It must be stored in RAM between time steps, and for *LSTMs* — the most common practical variant — the state is four times the size of the hidden dimension. A 128-unit LSTM holds 512 values of state, updated, for audio, 100 times a second. The operation count per time step is high, too — a 128-unit LSTM on 40-dimensional audio features is about 260,000 MACs per step, or 26 million per one-second window, comparable to a small CNN but with the additional state-management overhead. Where you can, embedded audio applications prefer 1D convolutions or depthwise separable convolutions over RNNs for exactly this reason.

Some applications do not need a neural network at all. For *structured* data — sensor readings with known features like temperature, pressure, vibration frequency — *decision trees* and *random forests* often match neural-network accuracy at a fraction of the cost. A decision tree is a series of *if-then* rules; inference is a single root-to-leaf path with one comparison per level. A 10-level binary tree has 1,023 nodes — about 4 KB of thresholds in flash, ten comparisons per inference, no activation buffers, no floating point. A random forest of 50 such trees needs ~200 KB and 500 comparisons, still cheaper than most neural networks. For anomaly detection, predictive maintenance, and binary classification on engineered features, decision trees are the right default. Move to a neural network when accuracy demands it and not before.

The trade is essentially this: trees are interpretable, fast, and small but require good feature engineering; neural networks can learn features from raw inputs (pixels, audio samples) but cost more in memory and compute. If your data is already structured, use a tree. If your data is raw and high-dimensional, use a network.

Whatever the architecture, three numbers determine deployment cost. The *parameter count* tells you flash usage — multiplied by bytes per parameter, which is 4 for float32 and 1 for int8. The *MAC count* (or FLOP count, similarly defined) tells you compute — divided by sustained processor throughput, that is your latency. The *activation memory* tells you RAM. These are not independent — pruning parameters reduces MACs and usually reduces activations — but the relationship is not always linear, and you should measure all three rather than estimating one from another. Every major framework reports them. TensorFlow has `tf.profiler` and the TFLite analyzer; PyTorch has `torchinfo.summary()` and `thop.profile()`; ONNX has `onnx.helper.printable_graph()`. The output lists each layer's parameter count, output shape, and operation count; sum them. A typical TFLite analyzer report looks like *model size: 1.2 MB; total parameters: 315,000; total MACs: 42 million; activation memory: 180 KB.* Now go back to Chapter 2's questions: does 1.2 MB fit in flash? Does 180 KB fit in RAM with the rest of the system? Can the processor do 42 M MACs inside the latency budget?

The translation between the two domains is essentially a vocabulary exchange. *Model size* is a flash requirement. *Parameter count* multiplied by bytes is the same flash requirement, said differently. *Activation memory* is a RAM requirement. *FLOPs* or *MAC count* divided by sustained throughput is a latency. *Quantization* is a memory and compute reduction at the cost of precision. *Pruning* reduces parameter and operation counts. *Batch size* is always 1 on embedded — there is no batch. When an ML engineer says *high memory footprint* they usually mean parameters plus activations; when you say *it doesn't fit in RAM* you mean activations exceed available SRAM. You are describing the same problem in the two languages of the same field. Learning to switch lets you ask for the right thing — *we need activation memory under 150 KB* — and accept the right answer back — *try MobileNetV2 with 0.35 width multiplier*.

The mapping from sensing task to model class is mostly conventional but worth stating. For *image classification, visual inspection, and object detection*, use a CNN; start with MobileNetV2 or V3, scale resolution and width multiplier until constraints are met, and try EfficientNet-Lite if you need more accuracy at similar cost. For *keyword spotting and audio classification*, prefer 1D CNNs or depthwise separable convolutions on spectrograms over RNNs; DS-CNN models hit 95%+ on standard keyword sets in under 100 KB of weights. For *time-series anomaly detection on sensor streams*, start with decision trees on engineered features (statistical moments, FFT magnitudes, autocorrelation); move to 1D CNNs or autoencoders only if raw streams are required. For *structured tabular data*, use trees or gradient-boosted trees; neural networks rarely beat them on small tabular datasets. For *gesture and motion classification* from accelerometers, use 1D CNNs if you have the RAM; use trees on hand-crafted features if you do not.

The pattern across all of these is the same one. Use the simplest model that meets the accuracy bar. Trees before networks. Feedforward before recurrent. Small CNNs before large. Every increment in model complexity costs memory, compute, and power, and only the increment that is *paid back* in accuracy is worth taking. The previous chapter taught you to read what the hardware can give. This chapter taught you to read what the model demands. The next chapter starts on the question those two together produce: how do you actually measure what an inference pass *costs* on the part you have, when the spec sheet and the architecture tell you what it ought to cost?

---

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

---

## 🕰️ AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Lotfi Zadeh** invented fuzzy logic — a way to make machines reason about "warmer," "almost full," "a little wobbly" — and it ran in millions of embedded controllers (cameras, rice cookers, subway brakes) long before deep learning shipped on microcontrollers.

**Run this:**

```
Who was Lotfi Zadeh, and how does his work on fuzzy logic and approximate reasoning connect to embedded machine learning today? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"Lotfi A. Zadeh"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain fuzzy logic in plain language, with one washing-machine example
- Ask it to compare a fuzzy controller to a small neural network solving the same control problem
- Add a constraint: "Answer as if you're writing a footnote in a textbook on embedded ML"

What changes? What gets better? What gets worse?
