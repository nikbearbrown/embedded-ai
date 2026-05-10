# Appendix A: Embedded Systems Quick Reference

This appendix provides reference materials for embedded systems constraint quantification, datasheet interpretation, and calculation workflows. Use these templates and worksheets when evaluating hardware for AI deployment.

## A.1 Constraint Quantification Template

Use this template to document the constraints for any embedded AI project. Fill in measured or specified values before model selection.

Project Information

Project name: _______________________

Application: _______________________

Date: _______________________

Target deployment date: _______________________

Functional Requirements

Task: (e.g., image classification, keyword spotting, anomaly detection)

Input type: (e.g., 96×96 RGB image, 1 kHz accelerometer, 16 kHz audio)

Output type: (e.g., 10-class classification, binary fault detection)

Required accuracy: ______ % (minimum acceptable)

Latency requirement: ______ ms (hard deadline / soft deadline)

Real-time class: (soft / firm / hard)

Memory Constraints

Target device: _______________________

Flash capacity: ______ KB / MB

Flash already used by firmware: ______ KB / MB

Flash available for model: ______ KB / MB

SRAM capacity: ______ KB / MB

SRAM used by firmware/stack/heap: ______ KB / MB

SRAM available for inference: ______ KB / MB

External memory: (none / PSRAM / SDRAM) ______ KB / MB

Compute Constraints

Processor type: (e.g., Cortex-M4, Cortex-M7, Cortex-A53)

Clock speed: ______ MHz

FPU: (yes / no)

SIMD extensions: (yes / no) — specify: _______________________

Estimated sustained throughput: ______ MMAC/s (measured or from benchmarks)

Latency budget: ______ ms

Acceptable latency margin: ______ % (e.g., 20% margin → use 80% of budget)

Power Constraints

Power source: (battery / mains / energy harvesting)

Battery type: _______________________

Battery capacity: ______ mAh at ______ V

Total battery energy: ______ Wh = ______ J

Target battery life: ______ days / months / years

Maximum average power: ______ mW

Active current (measured): ______ mA at ______ V

Sleep current (measured): ______ mA / µA at ______ V

Inference duty cycle: ______ % (active time / total time)

Communication Constraints

Connectivity: (WiFi / Bluetooth / LoRaWAN / cellular / none)

Bandwidth: ______ kbps / Mbps

Round-trip latency: ______ ms

Data transmission cost: ______ $/MB (if cellular)

Privacy constraints: (HIPAA / GDPR / proprietary / none)

Offline operation required: (yes / no)

Cost Constraints

Target unit cost: $ ______ (BOM)

Production volume: ______ units

Acceptable NRE (non-recurring engineering): $ ______

Safety and Regulatory

Safety-critical: (yes / no)

Applicable standards: (IEC 61508 / ISO 26262 / IEC 62304 / none)

Required SIL/ASIL: _______________________

Certification required: (FDA / CE Mark / FCC / none)

## A.2 Datasheet Reading Guide for AI Suitability

Step 1: Locate Memory Specifications

Where to look: Section titled "Memory," "Memory Map," or "Device Features"

Extract:

Flash capacity (KB or MB)

SRAM capacity (total)

SRAM partitioning (if specified: TCM, standard SRAM, cache)

External memory support (QSPI, SDRAM controller)

Red flags:

"Total memory" without flash/SRAM breakdown → likely hiding small SRAM

Cache listed as part of SRAM → subtract cache from available SRAM

No mention of external memory interface → cannot expand if on-chip is insufficient

AI relevance:

Flash must hold model weights + firmware

SRAM must hold activations + firmware heap/stack

TCM (if present) is ideal for activations (deterministic timing)

Step 2: Locate Processor Specifications

Where to look: Section titled "CPU Core," "Processor," or "Performance"

Extract:

Core type (Cortex-M0, M4, M7, A53, etc.)

Maximum clock speed (MHz or GHz)

Presence of FPU (floating-point unit)

Presence of DSP extensions or SIMD (e.g., Helium, NEON)

CoreMark score (if provided)

Red flags:

Clock speed listed as "up to X MHz" → may run slower in low-power modes

"FPU" without specifying single or double precision

No benchmark data (CoreMark, EEMBC) → performance is unknown

AI relevance:

FPU required for float32 inference efficiency

SIMD accelerates int8 inference by 4–8×

CoreMark gives rough CPU performance (higher is better, but not AI-specific)

Step 3: Locate Power Specifications

Where to look: Section titled "Electrical Characteristics," "Power Consumption," or "Operating Modes"

Extract:

Active current at maximum clock (mA)

Sleep mode current (µA or mA)

Deep sleep mode current (if available)

Current vs. clock speed curve (if provided)

Peripheral power consumption (camera, radio, sensors)

Red flags:

"Typical" current without "maximum" → typical is optimistic, use max for design

Sleep current specified at 25°C only → increases at higher temperatures

No breakdown of peripheral power → hard to estimate system power

AI relevance:

Active current × inference time = energy per inference

Sleep current × sleep time = baseline energy consumption

Duty cycle determines average power: (active_time × I_active + sleep_time × I_sleep) / total_time

Step 4: Locate AI-Specific Features (if claimed)

Where to look: Section titled "AI Accelerator," "Neural Processing," or marketing material

Extract:

Accelerator type (NPU, DSP, vector unit)

Supported operations (convolution, matrix multiply, etc.)

Claimed performance (TOPS, GOPS, MMAC/s)

Supported data types (int8, int16, float16)

Memory dedicated to accelerator

Red flags:

"AI-capable" with no performance numbers → marketing, not technical spec

TOPS claim without specifying data type → likely int8, not float32

No list of supported operations → may only accelerate subset of model

AI relevance:

Claimed TOPS must be verified with actual model profiling

Unsupported operations fall back to CPU → reduces effective speedup

Check vendor documentation for which models are optimized

Step 5: Check Errata and Application Notes

Where to look: Separate errata document (usually PDF on vendor website)

Extract:

Power consumption errata (e.g., "sleep current higher than specified")

Memory errata (e.g., "external SRAM interface has timing issue")

Peripheral errata that affect sensors or communication

Red flags:

Errata affecting power in sleep modes → destroys battery life calculations

Errata affecting memory performance → slows inference

No errata document available → chip is very new or vendor doesn't publish issues

AI relevance:

Power errata can invalidate battery life estimates

Memory errata can cause inference failures or crashes

## A.3 Memory Calculation Worksheet

Flash Memory Requirement

Component

Size (KB)

Notes

Firmware (base application)

______

Compile and check .map file

Inference engine (TFLite Micro, etc.)

______

~100 KB for TFLite Micro

Model weights (float32)

______

param_count × 4 bytes

Model weights (int8)

______

param_count × 1 byte

Preprocessing/postprocessing code

______

Feature extraction, NMS, etc.

Total flash required

______

Sum of above

Flash capacity

______

From datasheet

Margin

______

(capacity - required) / capacity × 100%

Acceptable margin: ≥20% (allows for future firmware updates)

SRAM Memory Requirement

Component

Size (KB)

Notes

Firmware heap

______

Typical: 10–50 KB

Firmware stack

______

Typical: 4–16 KB

RTOS overhead (if applicable)

______

FreeRTOS: ~10–20 KB

Communication buffers

______

UART, SPI, network buffers

Sensor buffers

______

ADC buffers, image buffers

Tensor arena (activations)

______

From TFLite or model profiling

Total SRAM required

______

Sum of above

SRAM capacity

______

From datasheet

Margin

______

(capacity - required) / capacity × 100%

Acceptable margin: ≥20% (SRAM usage grows during development)

Critical check: If total SRAM required > 80% of capacity, consider:

Reducing model size (pruning, smaller architecture)

Adding external PSRAM (if supported)

Reducing firmware buffer sizes

## A.4 Power Calculation Worksheet

Battery Energy Budget

Parameter

Value

Units

Battery capacity

______

mAh

Battery voltage

______

V

Total energy

______

Wh (= capacity × voltage / 1000)

Total energy

______

J (= Wh × 3600)

Target lifetime

______

days / months / years

Target lifetime

______

seconds

Maximum average power

______

mW (= total_energy_J / lifetime_s × 1000)

Duty Cycle Calculation

Operating Mode

Current (mA)

Time per Cycle (s)

Energy per Cycle (mJ)

Active (inference)

______

______

V × I_active × t_active

Sensor acquisition

______

______

V × I_sensor × t_sensor

Communication

______

______

V × I_comm × t_comm

Sleep

______

______

V × I_sleep × t_sleep

Total per cycle

—

______

______ (sum of above)

Cycle period: ______ seconds (e.g., inference every 10 seconds)

Average power: E_total_per_cycle / cycle_period = ______ mW

Battery life: total_energy_J / (average_power_mW / 1000) / 86400 = ______ days

Acceptable: Average power ≤ maximum average power from budget above.

Energy per Inference (Detailed)

Stage

Time (ms)

Current (mA)

Voltage (V)

Energy (mJ)

Wake from sleep

______

______

______

______

Sensor read

______

______

______

______

Preprocessing

______

______

______

______

Inference

______

______

______

______

Postprocessing

______

______

______

______

Communication

______

______

______

______

Return to sleep

______

______

______

______

Total

______

—

—

______

## A.5 Latency Calculation Worksheet

Theoretical Latency Estimate

Parameter

Value

Units

Model operation count

______

MACs or FLOPs

Processor sustained throughput

______

MMAC/s or GFLOPS

Theoretical latency

ops / throughput

milliseconds

Utilization factor

0.6–0.8

(accounts for memory overhead)

Estimated actual latency

theoretical / utilization

milliseconds

Measured Latency (On Target Hardware)

Run inference 100+ times and record:

Statistic

Value (ms)

Notes

Minimum

______

Best case

Mean

______

Average

Median

______

Middle value

95th percentile

______

95% of inferences complete by this time

Maximum

______

Worst case observed

Empirical WCET

max × 1.3

Max + 30% safety margin

Latency budget: ______ ms (from requirements)

Check: Empirical WCET < latency budget?

Yes → Latency constraint satisfied

No → Must reduce model size or upgrade processor

## A.6 Model Size Quick Reference

Parameter Count to Memory Size

Precision

Bytes per Parameter

100K params

500K params

1M params

5M params

float32

4

400 KB

2 MB

4 MB

20 MB

float16

2

200 KB

1 MB

2 MB

10 MB

int8

1

100 KB

500 KB

1 MB

5 MB

Typical Activation Memory (Rules of Thumb)

For CNNs on images:

96×96 input: 50–150 KB activations (int8), 200–600 KB (float32)

224×224 input: 500 KB – 2 MB activations (int8), 2–8 MB (float32)

For 1D CNNs on time series:

1000 samples input: 20–60 KB activations (int8)

10,000 samples input: 100–300 KB activations (int8)

For fully connected networks:

Activation memory ≈ largest layer output size × data type size

Note: These are rough estimates. Always profile actual models with TFLite or your inference framework.

A.7 Common Embedded AI Hardware Comparison

Device

Core

Clock

SRAM

Flash

FPU

SIMD

Sleep Current

Cost

Arduino Nano 33 BLE

M4

64 MHz

256 KB

1 MB

Yes

Yes

2.8 µA

$4

STM32L4R5

M4

120 MHz

640 KB

2 MB

Yes

Yes

0.4 µA

$6

STM32H743

M7

480 MHz

1 MB

2 MB

Yes

Yes

6 µA

$10

STM32N6

M55

800 MHz

2.5 MB

4 MB

Yes

Helium

10 µA

$14

nRF52840

M4

64 MHz

256 KB

1 MB

Yes

Yes

2.8 µA

$4

ESP32-S3

Xtensa

240 MHz

512 KB

8 MB

No

SIMD

10 µA

$4.50

Raspberry Pi Zero 2 W

4×A53

1 GHz

512 MB

SD card

Yes

NEON

100 mW

$15

Coral Dev Board Micro

M7

480 MHz

1 MB

64 MB

Yes

Yes

—

$60

Notes:

Sleep current is deep sleep / standby mode

Cost is approximate single-unit pricing (2024)

Coral Dev Board includes Edge TPU accelerator

## A.8 Constraint Checklist for Deployment Readiness

Before deploying a model to production, verify all constraints:

Memory

[ ] Model weights fit in flash with ≥20% margin

[ ] Activations fit in SRAM with ≥20% margin

[ ] Total firmware + model size measured and verified

[ ] No dynamic memory allocation during inference

[ ] Tensor arena size confirmed via profiling

Compute

[ ] Inference latency measured on target hardware (100+ runs)

[ ] Maximum observed latency < latency budget

[ ] Latency variance acceptable for application

[ ] No missed deadlines in stress testing

[ ] Processor runs at acceptable temperature under load

Power

[ ] Current draw measured during inference (not estimated)

[ ] Average power calculated from realistic duty cycle

[ ] Battery life meets requirement with ≥20% margin

[ ] Peak current does not exceed battery discharge limit

[ ] Sleep current confirmed (not just datasheet typical)

Accuracy

[ ] Validation accuracy ≥ application threshold

[ ] Accuracy measured on deployment-representative data

[ ] Accuracy after quantization verified (if quantized)

[ ] Edge cases tested (low light, noise, occlusions, etc.)

[ ] False positive and false negative rates acceptable

Integration

[ ] Model converted and tested on target framework

[ ] Firmware compiles without errors

[ ] No runtime errors or crashes in 1000+ inference runs

[ ] Output matches training model output (within tolerance)

[ ] Deployment toolchain documented

If any item is unchecked, deployment is not ready.

This appendix provides the calculation templates and reference tables needed for constraint-driven embedded AI design. Use these worksheets during hardware selection, model evaluation, and deployment validation.


---

*[<- Chapter 14](./chapter-14-integration-case-studies.md) | [Table of Contents](../README.md) | [Appendix B ->](./appendix-b-ml-quick-reference.md)*
