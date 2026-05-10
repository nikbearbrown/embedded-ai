# Appendix B: Machine Learning Quick Reference

This appendix provides a concise reference for machine learning concepts relevant to embedded AI deployment. Use this as a quick lookup when you encounter ML terminology in model documentation or research papers.

B.1 Core ML Concepts for Embedded Engineers

Supervised Learning

What it is: Training a model on labeled data (input-output pairs) to learn a mapping from inputs to outputs.

Example: Training an image classifier on 10,000 images labeled "cat," "dog," "car."

Embedded relevance: The trained model is what you deploy. The training process happens offline (on servers). You only deploy the inference function.

Key terms:

Training set: Data used to train the model

Validation set: Data used to tune hyperparameters

Test set: Data used to evaluate final performance

Overfitting: Model memorizes training data but fails on new data

Generalization: Model performs well on data it hasn't seen

Inference vs. Training

Training: Adjusting model weights to minimize error on labeled data. Requires backpropagation, gradient computation, and iterative optimization. Expensive (GPU-hours to GPU-days).

Inference: Running the trained model on new inputs to produce predictions. No weight updates. Cheap (milliseconds per input).

Embedded relevance: You only deploy inference. Training happens on powerful machines with GPUs. Your embedded device never trains—it only runs the frozen model.

Memory comparison:

Training: Needs weights + activations + gradients + optimizer state (3–5× model size)

Inference: Needs weights + activations only

Model, Weights, and Parameters

Model: The architecture—the sequence of layers and operations (e.g., "MobileNetV2 with 10 output classes").

Weights (or parameters): The learned values that define the model's behavior. After training, weights are fixed numbers stored in the model file.

Parameter count: Total number of weights. Determines model size in memory (param_count × bytes_per_param).

Embedded relevance: Parameter count determines flash usage. Weights are read-only data during inference.

Layers, Activations, and Forward Pass

Layer: A single operation in the network (convolution, matrix multiply, activation function).

Activation: The output of a layer. Also called "feature map" or "tensor."

Forward pass (inference): Data flows from input through all layers to output. Each layer reads its input activation, applies its operation, and produces an output activation.

Embedded relevance: Activations consume SRAM during inference. Activation memory is the hidden memory cost that datasheets don't show.

Loss Function and Accuracy

Loss function: A measure of how wrong the model's predictions are during training. Examples: cross-entropy (for classification), mean squared error (for regression).

Accuracy: Fraction of predictions that are correct (for classification). Example: 90% accuracy = 90 correct out of 100 predictions.

Embedded relevance: You care about accuracy (does the model work?), not loss (which is a training-time concept). Validation accuracy is what you report in deployment documentation.

## B.2 Common Neural Network Architectures

Fully Connected (Dense) Layers

What they do: Connect every input to every output via learned weights. Operation: y = W × x + b

Use case: Final classification layers, small networks for tabular data.

Cost: High parameter count. A layer with 1000 inputs and 1000 outputs has 1 million weights.

Embedded suitability: Expensive in memory. Use sparingly.

Convolutional Layers (Conv2D)

What they do: Apply a small filter (e.g., 3×3) that slides across the input, detecting local patterns like edges or textures.

Use case: Image processing, computer vision.

Cost: Moderate parameter count but high operation count. A 3×3 conv with 32 input channels and 64 output channels on a 96×96 image: 64M operations.

Embedded suitability: Efficient for images. Use depthwise separable convolutions for lower cost.

Depthwise Separable Convolutions

What they do: Split standard convolution into two steps: depthwise (filter each channel independently) + pointwise (mix channels with 1×1 conv).

Use case: Efficient image classification (MobileNet, EfficientNet).

Cost: 8–9× fewer operations than standard convolution for similar accuracy.

Embedded suitability: Excellent. Standard architecture for embedded vision.

Pooling Layers (MaxPool, AvgPool)

What they do: Downsample feature maps by taking the max or average in each region (e.g., 2×2 pooling reduces 96×96 to 48×48).

Use case: Reduce spatial resolution in CNNs.

Cost: Negligible operations. Reduces activation memory (smaller feature maps).

Embedded suitability: Good. Reduces memory and compute.

Recurrent Layers (RNN, LSTM, GRU)

What they do: Process sequences by maintaining a hidden state that carries information from previous time steps.

Use case: Time-series, audio, text.

Cost: High memory (state must persist across time steps). High operations (matrix multiply at each time step).

Embedded suitability: Difficult. State memory grows with sequence length. Prefer 1D CNNs or decision trees when possible.

Activation Functions

ReLU (Rectified Linear Unit): f(x) = max(0, x). Fast, standard choice.

Sigmoid: f(x) = 1 / (1 + e^(-x)). Slow (requires exp). Used in older networks.

Softmax: Converts outputs to probabilities (sum = 1). Used for classification.

Embedded relevance: ReLU is cheap (one comparison). Sigmoid/tanh are expensive (require exp/division). Use ReLU when possible.

B.3 ML-to-Embedded Vocabulary Translation

ML Term

Embedded Equivalent

What It Means for You

Model size

Flash memory requirement

How much non-volatile storage the weights need

Parameter count

Weight memory

Number of learned values × bytes per value

FLOP count

Compute operations

How many arithmetic operations inference requires

Activation memory

RAM requirement

Working memory needed during inference

Inference latency

Execution time

How long it takes to process one input

Batch size

Number of parallel inputs

Always 1 on embedded (no batching)

Quantization

Reducing numeric precision

float32 → int8 saves 75% memory

Pruning

Removing weights

Reduces parameter count and operations

Epoch

Full pass through training data

Training concept—not relevant to deployment

Learning rate

Training hyperparameter

Training concept—not relevant to deployment

Overfitting

Model memorizes training data

Test accuracy < training accuracy—bad generalization

Validation accuracy

Performance on held-out data

The metric you report for deployed models

Ground truth

Correct label

What the model should predict

False positive

Incorrect "yes" prediction

Alarm when there's no fault

False negative

Incorrect "no" prediction

Miss a fault that is present

Precision

TP / (TP + FP)

Of all positive predictions, how many were correct?

Recall (Sensitivity)

TP / (TP + FN)

Of all actual positives, how many did we detect?

F1 score

Harmonic mean of precision and recall

Balanced metric for imbalanced datasets

## B.4 Common Model Architectures for Embedded

For Image Classification (96×96 to 224×224)

Recommended:

MobileNetV2 (variants: 0.35, 0.5, 0.75, 1.0 width multiplier)

MobileNetV3-Small

EfficientNet-Lite (Lite0, Lite1)

SqueezeNet

Typical sizes:

MobileNetV2-0.35: 400K params, 25M MACs, ~88% accuracy

MobileNetV2-1.0: 3.5M params, 300M MACs, ~90% accuracy

EfficientNet-Lite0: 4.6M params, 400M MACs, ~92% accuracy

When to use: Camera-based sensing, visual inspection, gesture recognition (from images).

For Audio Classification (Keyword Spotting, Sound Events)

Recommended:

DS-CNN (Depthwise Separable CNN on spectrograms)

1D CNN on raw audio or MFCCs

Small LSTM (if SRAM allows)

Typical sizes:

DS-CNN: 100K params, 10M MACs, 95%+ accuracy on Google Speech Commands

1D CNN: 50K params, 8M MACs, 92% accuracy

When to use: Voice interfaces, acoustic event detection, environmental sound classification.

For Time-Series Anomaly Detection

Recommended:

Random forest on engineered features

1D CNN on raw sequences

Autoencoder (if unsupervised)

Typical sizes:

Random forest: 200 KB, <1 ms inference, 85–90% accuracy

1D CNN: 100K params, 12M MACs, 92% accuracy

Autoencoder: 500K params, 30M MACs, 88% accuracy

When to use: Vibration monitoring, sensor fault detection, predictive maintenance.

For Gesture Recognition (Accelerometer, Gyroscope)

Recommended:

1D CNN on raw sensor data

Random forest on statistical features

Small LSTM (for complex temporal patterns)

Typical sizes:

1D CNN: 64K params, 8M MACs, 90%+ accuracy

Random forest: 180 KB, 0.5 ms, 88% accuracy

When to use: Wearables, fitness trackers, human activity recognition.

B.5 Quantization Quick Reference

Precision Levels

Type

Bits

Range

Memory

Accuracy Impact

Embedded Support

float32

32

±3.4×10³⁸

4 bytes

Baseline (0%)

Good (FPU needed)

float16

16

±6.5×10⁴

2 bytes

0–1% loss

Poor on MCUs

int16

16

-32,768 to 32,767

2 bytes

1–3% loss

Good (SIMD helps)

int8

8

-128 to 127

1 byte

3–10% loss

Excellent (SIMD 4×)

Post-Training Quantization (PTQ)

What it does: Converts a trained float32 model to int8 without retraining.

How it works: Run model on calibration dataset (100–1000 samples) to measure weight and activation ranges. Compute scale/zero_point. Convert weights to int8.

When to use: You don't have access to training code or dataset.

Accuracy cost: 3–10% typical.

Code (TensorFlow Lite):

converter.optimizations = [tf.lite.Optimize.DEFAULT]

converter.representative_dataset = calibration_data_gen

Quantization-Aware Training (QAT)

What it does: Simulates quantization during training so the model learns to be robust to quantization errors.

When to use: Accuracy is critical and PTQ degrades too much.

Accuracy cost: 1–3% typical.

Tradeoff: Requires retraining (hours to days).

## B.6 Model Evaluation Metrics

For Classification Tasks

Accuracy: (TP + TN) / (TP + TN + FP + FN)

 Use when: Classes are balanced (roughly equal number of samples per class).

Precision: TP / (TP + FP)

 Use when: False positives are costly (e.g., spam detection—don't want to block real emails).

Recall (Sensitivity): TP / (TP + FN)

 Use when: False negatives are costly (e.g., disease detection—don't want to miss a sick patient).

F1 Score: 2 × (Precision × Recall) / (Precision + Recall)

 Use when: You want a single metric that balances precision and recall.

Confusion Matrix:

               Predicted

                Pos    Neg

Actual  Pos    TP     FN

        Neg    FP     TN

Example for embedded:

 Fault detection with 95% recall and 90% precision:

Of 100 faults, 95 are detected (5 missed = false negatives)

Of 100 fault predictions, 90 are correct (10 are false alarms = false positives)

For Regression Tasks

Mean Absolute Error (MAE): Σ |predicted - actual| / N

 Use when: You want error in the same units as the output.

Mean Squared Error (MSE): Σ (predicted - actual)² / N

 Use when: Large errors should be penalized more than small errors.

R² Score: Fraction of variance explained by the model.

 Use when: You want a normalized metric (0 = bad, 1 = perfect).

## B.7 Common Pitfalls and How to Avoid Them

Pitfall 1: Using ImageNet Accuracy to Select Models

Why it's wrong: ImageNet is 1000 classes of high-resolution photos. Your application might be 3 classes of 96×96 industrial images. A model with 90% ImageNet accuracy might have 70% accuracy on your data.

Fix: Always validate on your deployment dataset, not benchmark datasets.

Pitfall 2: Assuming Quantization Is Free

Why it's wrong: Quantization introduces numerical errors. Some models tolerate int8 with <1% loss. Others degrade by 10%+.

Fix: Measure accuracy before and after quantization. If loss > 5%, try QAT or mixed precision.

Pitfall 3: Confusing Parameter Count with Inference Cost

Why it's wrong: A model with 1M parameters might run faster than a model with 500K parameters if the 500K-param model has expensive operations (e.g., large convolutions).

Fix: Profile actual latency on target hardware. Don't rely on parameter count alone.

Pitfall 4: Training on Clean Data, Deploying on Noisy Data

Why it's wrong: Training data is often cleaner than real-world data (better lighting, less occlusion, calibrated sensors). Models overfit to clean data and fail on noisy inputs.

Fix: Add data augmentation during training (noise, blur, rotation) and validate on realistic noisy data.

Pitfall 5: Ignoring Class Imbalance

Why it's wrong: If your dataset has 95% "normal" and 5% "fault," a dumb model that always predicts "normal" achieves 95% accuracy but is useless.

Fix: Use balanced datasets or report precision/recall instead of accuracy. For imbalanced data, F1 score is a better metric.

B.8 Where to Find Pretrained Models

Model Zoos

TensorFlow Model Garden: https://github.com/tensorflow/models

 Includes MobileNet, EfficientNet, ResNet for image classification.

PyTorch Hub: https://pytorch.org/hub/

 Pretrained models loadable with torch.hub.load().

ONNX Model Zoo: https://github.com/onnx/models

 Framework-agnostic models in ONNX format.

Edge Impulse Public Projects: https://edgeimpulse.com/

 Community-contributed models for embedded AI.

When to Use Pretrained Models

Use pretrained when:

Your dataset is small (<1,000 samples)

Your task is similar to ImageNet (object recognition)

You want to fine-tune final layers only

Train from scratch when:

Your dataset is large (>10,000 samples)

Your task is very different from ImageNet (industrial defects, medical images)

You need a custom architecture for size constraints

## B.9 Debugging Checklist for Deployed Models

If your deployed model produces incorrect results:

1. Verify Input Preprocessing

[ ] Input normalization matches training (e.g., [0,1] vs. [-1,1])

[ ] Input dimensions match model input shape

[ ] Color channel order correct (RGB vs. BGR)

[ ] Quantization applied to input (if model expects int8 input)

2. Verify Model Conversion

[ ] Converted model accuracy matches original (test in Python/TFLite interpreter)

[ ] All layers converted successfully (check converter logs)

[ ] Quantization parameters correct (scale, zero_point)

3. Verify Inference Engine

[ ] Correct ops registered in OpResolver

[ ] Tensor arena size sufficient (no allocation errors)

[ ] Output dequantization applied (if model outputs int8)

4. Compare Outputs

[ ] Run same input through training model and deployed model

[ ] Check output tensor values (not just final classification)

[ ] Allow for small numerical differences due to quantization (±1–2%)

If outputs differ by >5%, something is wrong. Trace back through the pipeline.

This appendix provides the ML knowledge needed to evaluate, select, and deploy models without requiring deep ML expertise. For deeper learning, see Deep Learning by Goodfellow et al. or Stanford's CS231n course notes.


---

*[<- Appendix A](./appendix-a-embedded-quick-reference.md) | [Table of Contents](../README.md) | [Appendix C ->](./appendix-c-hardware-reference.md)*
