# Appendix D: Toolchain Setup Guides

This appendix provides step-by-step setup instructions for the three most common embedded AI toolchains: TensorFlow Lite for Microcontrollers, Edge Impulse, and STM32Cube.AI.

Note: Toolchain versions and installation steps change frequently. Check official documentation for the latest instructions. This guide is current as of 2024–2025.

## D.1 TensorFlow Lite for Microcontrollers Setup

TensorFlow Lite for Microcontrollers (TFLite Micro) is the most widely used inference engine for embedded AI. It runs on bare-metal systems and RTOSs with minimal dependencies.

Prerequisites

OS: Linux, macOS, or Windows (WSL recommended for Windows)

Tools: Git, Python 3.8+, Make, GCC or ARM toolchain

Hardware: Development board (Arduino Nano 33 BLE, STM32 Nucleo, etc.)

Step 1: Install TensorFlow (for Model Training and Conversion)

# Create a virtual environment (recommended)
python3 -m venv tflite-env

source tflite-env/bin/activate  # On Windows: tflite-env\Scripts\activate

# Install TensorFlow
pip install tensorflow==2.14.0

# Verify installation
python -c "import tensorflow as tf; print(tf.__version__)"

Step 2: Clone TensorFlow Repository (for TFLite Micro)

git clone https://github.com/tensorflow/tflite-micro.git

cd tflite-micro

The tflite-micro repository contains the inference library, examples, and build system.

Step 3: Convert a Trained Model to TFLite

Assuming you have a trained Keras model (my_model.h5):

import tensorflow as tf

# Load model
model = tf.keras.models.load_model('my_model.h5')

# Create converter
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Enable int8 quantization
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Provide calibration dataset (generator function)
def representative_dataset():

    for i in range(100):

        # Load sample input (e.g., 96x96x3 image)

        sample = load_sample(i)  # Replace with your data loader

        yield [sample.astype('float32')]

converter.representative_dataset = representative_dataset

# Set input/output to int8
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]

converter.inference_input_type = tf.int8

converter.inference_output_type = tf.int8

# Convert
tflite_model = converter.convert()

# Save
with open('my_model.tflite', 'wb') as f:

    f.write(tflite_model)

print("Model converted to my_model.tflite")

Step 4: Convert TFLite Model to C Array

# Use xxd to convert binary to C header
xxd -i my_model.tflite > my_model_data.h

This creates a C header file with the model as a byte array:

unsigned char my_model_tflite[] = {

  0x18, 0x00, 0x00, 0x00, 0x54, 0x46, 0x4c, 0x33, ...

};

unsigned int my_model_tflite_len = 123456;

Step 5: Build and Flash for Arduino Nano 33 BLE Sense

Option A: Using Arduino IDE

Install Arduino IDE (version 2.0+).

Install TensorFlow Lite Arduino library:

Go to Tools → Manage Libraries

Search for "Arduino_TensorFlowLite"

Install version compatible with your TensorFlow version

Create a sketch:

#include <TensorFlowLite.h>
#include "my_model_data.h"

// Tensor arena (adjust size based on model)

constexpr int kTensorArenaSize = 80 * 1024;

alignas(16) uint8_t tensor_arena[kTensorArenaSize];

tflite::MicroInterpreter* interpreter = nullptr;

void setup() {

    Serial.begin(115200);

    // Load model

    const tflite::Model* model = tflite::GetModel(my_model_tflite);

    // Create op resolver (add all ops your model uses)

    static tflite::MicroMutableOpResolver<10> resolver;

    resolver.AddConv2D();

    resolver.AddDepthwiseConv2D();

    resolver.AddFullyConnected();

    resolver.AddSoftmax();

    resolver.AddReshape();

    resolver.AddQuantize();

    resolver.AddDequantize();

    // Add more ops as needed

    // Create interpreter

    static tflite::MicroInterpreter static_interpreter(

        model, resolver, tensor_arena, kTensorArenaSize);

    interpreter = &static_interpreter;

    // Allocate tensors

    TfLiteStatus allocate_status = interpreter->AllocateTensors();

    if (allocate_status != kTfLiteOk) {

        Serial.println("AllocateTensors() failed");

        return;

    }

    Serial.println("Model loaded successfully");

}

void loop() {

    // Get input tensor

    TfLiteTensor* input = interpreter->input(0);

    // Fill input with data (example: zeros)

    for (int i = 0; i < input->bytes; i++) {

        input->data.int8[i] = 0;

    }

    // Run inference

    TfLiteStatus invoke_status = interpreter->Invoke();

    if (invoke_status != kTfLiteOk) {

        Serial.println("Invoke() failed");

        return;

    }

    // Read output

    TfLiteTensor* output = interpreter->output(0);

    int8_t max_score = -128;

    int predicted_class = 0;

    for (int i = 0; i < output->dims->data[1]; i++) {

        if (output->data.int8[i] > max_score) {

            max_score = output->data.int8[i];

            predicted_class = i;

        }

    }

    Serial.print("Predicted class: ");

    Serial.println(predicted_class);

    delay(1000);

}

Compile and upload to Arduino Nano 33 BLE Sense.

Option B: Using PlatformIO (for more control)

Install PlatformIO (VS Code extension or CLI).

Create a new project:

pio init --board nano_33_ble

Add TensorFlow Lite library to platformio.ini:

[env:nano_33_ble]

platform = nordicnrf52

board = nano_33_ble

framework = arduino

lib_deps = 

    https://github.com/tensorflow/tflite-micro-arduino-examples

Copy your model header (my_model_data.h) to src/.

Write sketch as above and build:

pio run --target upload

Step 6: Verify Inference on Device

Connect to serial monitor (115200 baud) and observe output. Compare predictions to expected results.

Common issues:

AllocateTensors() failed: Tensor arena too small. Increase kTensorArenaSize.

Op not found: Missing operation in OpResolver. Add the missing op.

Wrong output: Quantization mismatch or input preprocessing issue.

## D.2 Edge Impulse Setup

Edge Impulse is a web-based platform that handles the full pipeline: data collection, training, optimization, and deployment.

Prerequisites

Account: Create free account at https://edgeimpulse.com

Browser: Chrome or Firefox (for data collection)

Hardware: Compatible device (Arduino Nano 33 BLE, STM32, ESP32, Raspberry Pi)

Step 1: Install Edge Impulse CLI

# Install Node.js (if not already installed)
# Download from https://nodejs.org (LTS version recommended)

# Install Edge Impulse CLI
npm install -g edge-impulse-cli --force

# Verify installation
edge-impulse-version

Step 2: Connect Your Device

For Arduino Nano 33 BLE Sense:

Flash Edge Impulse firmware:

Download firmware from https://docs.edgeimpulse.com/docs/development-platforms/officially-supported-mcu-targets/arduino-nano-33-ble-sense

Upload using Arduino IDE or arduino-cli

Connect device via USB and run:

edge-impulse-daemon

Follow prompts to log in and select your project.

For custom devices:

 Use edge-impulse-data-forwarder to stream data from custom firmware.

Step 3: Collect Data

Via Web Interface:

Go to Data acquisition tab

Click Collect data

Select device and sample length

Label samples (e.g., "gesture_1", "gesture_2")

Collect 50–100 samples per class

Via CLI:

edge-impulse-uploader --category training image1.jpg

edge-impulse-uploader --category testing image2.jpg

Step 4: Design Impulse (Preprocessing + Model)

Go to Impulse design tab

Add processing block:

For images: Image (resize, crop)

For audio: Audio (MFCC) or Audio (Spectrogram)

For sensors: Spectral features or Raw data

Add learning block:

Classification (for labeling)

Transfer learning (images) (MobileNetV2-based)

Keras (custom architecture)

Click Save Impulse

Step 5: Generate Features and Train

Go to Spectral features (or your chosen processing block)

Click Generate features

Go to Classifier (or your learning block)

Configure model settings (layers, learning rate—or use defaults)

Click Start training

Wait for training to complete (1–30 minutes depending on dataset size)

Step 6: Test and Validate

Go to Model testing tab

Click Classify all

Review accuracy, confusion matrix

If accuracy is low, collect more data or tune model

Step 7: Deploy to Device

Go to Deployment tab

Select target:

Arduino library (for Arduino/PlatformIO)

C++ library (for custom firmware)

Firmware (for supported boards—pre-built binary)

Click Build

Download the deployment package (ZIP file)

For Arduino library:

Unzip the package

Copy folder to Arduino libraries/ directory

Restart Arduino IDE

Open example sketch: File → Examples → YourProjectName → nano_ble33_sense

For firmware:

Flash directly using edge-impulse-run-impulse (for supported boards)

Step 8: Run Inference

Flash the deployment firmware and run. Edge Impulse includes built-in serial output showing classification results.

Example output:

Predictions:

  gesture_1: 0.92

  gesture_2: 0.05

  gesture_3: 0.03

## D.3 STM32Cube.AI Setup

STM32Cube.AI is STMicroelectronics' tool for converting and optimizing models for STM32 microcontrollers, including those with integrated NPUs.

Prerequisites

OS: Windows or Linux

Tools: STM32CubeIDE (includes Cube.AI), STM32CubeMX

Hardware: STM32 development board (Nucleo, Discovery)

Step 1: Install STM32CubeIDE

Download from https://www.st.com/en/development-tools/stm32cubeide.html

Install (requires registration—free ST account)

Launch STM32CubeIDE

Step 2: Install X-CUBE-AI Expansion Package

Open STM32CubeMX (embedded in CubeIDE)

Go to Help → Manage Embedded Software Packages

Expand STMicroelectronics → X-CUBE-AI

Select latest version and click Install Now

Step 3: Create New Project

File → New → STM32 Project

Select your board (e.g., NUCLEO-H743ZI)

Name project (e.g., "my_ai_project")

Click Finish

Step 4: Enable X-CUBE-AI in CubeMX

In CubeMX view, go to Software Packs → Select Components

Expand STMicroelectronics.X-CUBE-AI

Check Core and Validation

Click OK

Go to Middleware → X-CUBE-AI

Enable Artificial Intelligence X-CUBE-AI

Step 5: Add Your Model

In X-CUBE-AI configuration pane, click Add network

Browse to your model file:

Supported: .tflite, .onnx, .h5 (Keras)

Set network name (e.g., "my_model")

Click Analyze

Cube.AI will analyze the model and show:

RAM requirement

Flash requirement

Estimated latency (MACC count)

Supported/unsupported operations

Step 6: Optimize Model (Optional)

In Model settings, enable:

Compression: Reduces model size

Quantization: Converts to int8 (if model is still float32)

Click Validate on target to measure actual latency on hardware

Step 7: Generate Code

Click GENERATE CODE in top-right

Cube.AI generates:

X-CUBE-AI/App/: Application code

Middlewares/ST/AI/: Inference library

Model header file: network.h, network_data.h

Step 8: Write Application Code

Open X-CUBE-AI/App/app_x-cube-ai.c and modify the inference loop:

#include "ai_platform.h"
#include "network.h"
#include "network_data.h"

static ai_handle network = AI_HANDLE_NULL;

AI_ALIGNED(4) static ai_u8 activations[AI_NETWORK_DATA_ACTIVATIONS_SIZE];

void MX_X_CUBE_AI_Init(void) {

    ai_error err;

    // Create network

    err = ai_network_create(&network, AI_NETWORK_DATA_CONFIG);

    if (err.type != AI_ERROR_NONE) {

        printf("ai_network_create error\n");

        return;

    }

    // Initialize network

    ai_network_params params = {

        AI_NETWORK_DATA_WEIGHTS(ai_network_data_weights_get()),

        AI_NETWORK_DATA_ACTIVATIONS(activations)

    };

    if (!ai_network_init(network, &params)) {

        printf("ai_network_init error\n");

        return;

    }

    printf("Network initialized\n");

}

void MX_X_CUBE_AI_Process(void) {

    ai_i32 nbatch;

    ai_float input_data[AI_NETWORK_IN_1_SIZE];

    ai_float output_data[AI_NETWORK_OUT_1_SIZE];

    // Fill input_data with sensor readings

    // ...

    // Create input/output buffers

    ai_buffer ai_input[1] = AI_NETWORK_IN;

    ai_buffer ai_output[1] = AI_NETWORK_OUT;

    ai_input[0].data = AI_HANDLE_PTR(input_data);

    ai_output[0].data = AI_HANDLE_PTR(output_data);

    // Run inference

    nbatch = ai_network_run(network, ai_input, ai_output);

    if (nbatch != 1) {

        printf("ai_network_run error\n");

        return;

    }

    // Process output

    for (int i = 0; i < AI_NETWORK_OUT_1_SIZE; i++) {

        printf("Output[%d]: %f\n", i, output_data[i]);

    }

}

Step 9: Build and Flash

Click Build (hammer icon) in CubeIDE

Connect STM32 board via ST-Link

Click Run (play icon) to flash

Monitor output via serial terminal (115200 baud)

Step 10: Validation on Target (Optional)

Cube.AI can validate the model on actual hardware:

In CubeMX, go to X-CUBE-AI → Validation

Select validation method:

On Desktop: Simulate (fast but approximate)

On Target: Measure actual latency and accuracy on board

Click Validate

This compares the embedded model's output to the original model's output and measures latency.

## D.4 Common Toolchain Issues and Solutions

TensorFlow Lite Micro

Issue: AllocateTensors() fails with "insufficient memory"

 Solution: Increase kTensorArenaSize. Check model's activation memory requirement using TFLite analyzer.

Issue: "Op not registered" error

 Solution: Add missing operation to MicroMutableOpResolver. Check converter logs for full list of ops used.

Issue: Output is all zeros or garbage

 Solution: Check input quantization. If model expects int8 input, ensure input data is quantized (not raw float).

Edge Impulse

Issue: Low accuracy after training

 Solution: Collect more data (50+ samples per class). Ensure data is diverse (different lighting, positions, etc.).

Issue: Device not detected by edge-impulse-daemon

 Solution: Install USB drivers. On Windows, install STM32 Virtual COM Port driver or Arduino drivers.

Issue: Deployment firmware too large for target

 Solution: Use quantized int8 model instead of float32. Reduce model size (fewer layers or smaller architecture).

STM32Cube.AI

Issue: Model analysis shows "unsupported operation"

 Solution: Some operations are not supported by Cube.AI. Simplify model architecture or use a different operation (e.g., replace PReLU with ReLU).

Issue: Validation fails with large numerical errors

 Solution: Quantization issue. Use quantization-aware training (QAT) instead of post-training quantization.

Issue: Latency on target is much higher than estimated

 Solution: Cube.AI estimates assume optimal conditions. Real latency includes memory access overhead. Enable hardware accelerator if available (e.g., STM32N6 NPU).

D.5 Toolchain Comparison Summary

Feature

TFLite Micro

Edge Impulse

STM32Cube.AI

Ease of use

Medium (requires coding)

Easy (web-based GUI)

Medium (IDE-integrated)

Flexibility

High (full control)

Medium (limited arch)

Medium (STM32 only)

Model formats

TFLite

TFLite, ONNX, Keras

TFLite, ONNX, Keras

Hardware support

Any (with C++ compiler)

30+ boards

STM32 only

Optimization

Manual (quantization)

Automatic

Automatic + NPU support

Documentation

Excellent (TensorFlow docs)

Excellent (built-in)

Good (ST docs)

Cost

Free (open source)

Free tier, paid for teams

Free

Best for

Custom deployments

Rapid prototyping

STM32 production

## D.6 Next Steps After Setup

Once your toolchain is set up:

Validate on target: Always measure latency, memory, and accuracy on actual hardware. Simulation is not sufficient.

Optimize iteratively: If constraints are tight, optimize the model (quantization, pruning) and re-deploy.

Document your pipeline: Record model version, conversion settings, and deployment steps for reproducibility.

Version control: Store model files, conversion scripts, and firmware in Git.

Toolchains evolve rapidly. For the latest setup instructions, always consult:

TensorFlow Lite Micro: https://github.com/tensorflow/tflite-micro

Edge Impulse: https://docs.edgeimpulse.com

STM32Cube.AI: https://www.st.com/en/embedded-software/x-cube-ai.html

This appendix will be updated on the book's companion website as toolchains change.

ThThis is the book contents now add all this


---

*[<- Appendix C](./appendix-c-hardware-reference.md) | [Table of Contents](../README.md)*
