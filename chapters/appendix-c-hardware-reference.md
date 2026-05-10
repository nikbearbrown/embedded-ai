# Appendix C: Hardware Reference — AI-Capable Microcontroller and SoC Comparison

This appendix provides detailed specifications for embedded AI hardware platforms. Use this table to compare options when selecting hardware for deployment.

Note: Specifications are current as of 2024–2025. Check vendor datasheets for latest information, as chip availability and pricing change frequently.

## C.1 Microcontroller Comparison Table

Ultra-Low-Power Microcontrollers (Battery-Optimized)

Spec

nRF52840

STM32L4R5

STM32L4S5

STM32U585

Vendor

Nordic Semi

STMicro

STMicro

STMicro

Core

Cortex-M4

Cortex-M4

Cortex-M4

Cortex-M33

Clock (max)

64 MHz

120 MHz

120 MHz

160 MHz

Flash

1 MB

2 MB

2 MB

2 MB

SRAM

256 KB

640 KB

640 KB

786 KB

FPU

Single

Single

Single

Single

SIMD/DSP

Yes

Yes

Yes

Helium (MVE)

AI Accelerator

No

No

No

No

Active current

5.3 mA @ 64 MHz

100 µA/MHz

100 µA/MHz

62 µA/MHz

Sleep current

2.8 µA

0.4 µA

0.4 µA

0.16 µA

Connectivity

BLE 5.3, NFC

None

None

None

Typical use

BLE wearables, IoT

Ultra-low-power sensors

Ultra-low-power sensors

Secure IoT

Cost (est.)

$4

$6

$8

$12

Availability

Excellent

Excellent

Good

Good

Selection notes:

nRF52840: Best for BLE applications. Moderate SRAM (256 KB) limits model size.

STM32L4R5: Best sleep current. Large SRAM (640 KB) supports moderate-sized models.

STM32U585: TrustZone for secure boot. Helium SIMD accelerates int8/int16 inference.

High-Performance Microcontrollers (Compute-Optimized)

Spec

STM32H743

STM32H7A3

STM32H7B3

STM32N6

Vendor

STMicro

STMicro

STMicro

STMicro

Core

Cortex-M7

Cortex-M7

Cortex-M7

Cortex-M55

Clock (max)

480 MHz

280 MHz

280 MHz

800 MHz

Flash

2 MB

2 MB

2 MB

4 MB

SRAM

1 MB

1.4 MB

1.4 MB

2.5 MB

FPU

Double

Double

Double

Single

SIMD/DSP

Yes

Yes

Yes

Helium (MVE)

AI Accelerator

No

No

No

Yes (3 TOPS int8)

Active current

~150 mA @ 480 MHz

~100 mA @ 280 MHz

~100 mA @ 280 MHz

~200 mA @ 800 MHz

Sleep current

6 µA

2.5 µA

2.5 µA

10 µA

External mem

Yes (QSPI, SDRAM)

Yes (QSPI, Octo-SPI)

Yes

Yes

Typical use

Vision, motor control

Industrial AI

Displays + AI

On-device vision

Cost (est.)

$10

$12

$14

$16

Availability

Excellent

Good

Good

Limited (new)

Selection notes:

STM32H743: Workhorse for embedded AI. 480 MHz + 1 MB SRAM handles medium models.

STM32H7A3: Larger SRAM (1.4 MB) for bigger models. Lower clock saves power.

STM32N6: Integrated NPU. Best latency for vision. Higher cost.

WiFi/BLE SoCs (Wireless-Integrated)

Spec

ESP32-S3

ESP32-C6

nRF5340

Vendor

Espressif

Espressif

Nordic Semi

Core

Dual Xtensa LX7

RISC-V

Dual M33 (app + net)

Clock (max)

240 MHz

160 MHz

128 MHz / 64 MHz

Flash

External (typ. 8 MB)

External (typ. 4 MB)

1 MB

SRAM

512 KB

512 KB

512 KB

FPU

No

No

Single

SIMD/DSP

Vector ext.

Vector ext.

Yes

AI Accelerator

AI instructions

AI instructions

No

Active current

40 mA @ 240 MHz

25 mA @ 160 MHz

8 mA @ 128 MHz

Sleep current

10 µA

7 µA

2.8 µA

Connectivity

WiFi 4, BLE 5

WiFi 6, BLE 5.3, Zigbee

BLE 5.3

Typical use

WiFi cameras, gateways

IoT gateways

BLE sensors, wearables

Cost (est.)

$4.50

$3.50

$8

Availability

Excellent

Excellent

Excellent

Selection notes:

ESP32-S3: Best price/performance for WiFi + AI. AI instructions accelerate some ops. No FPU limits float32 performance.

nRF5340: Dual-core (app + network) allows BLE to run independently. Best for ultra-low-power BLE + AI.

C.2 Application Processors and Edge Compute

Spec

Raspberry Pi Zero 2 W

Raspberry Pi 4B

NVIDIA Jetson Nano

Google Coral Dev Board

Core

4× Cortex-A53

4× Cortex-A72

4× Cortex-A57

4× Cortex-A53

Clock

1 GHz

1.5 GHz

1.43 GHz

1.5 GHz

RAM

512 MB

1–8 GB

2–4 GB

1 GB

GPU

VideoCore IV

VideoCore VI

128-core Maxwell

GC7000Lite

AI Accelerator

No

No

Yes (128 CUDA cores)

Yes (Edge TPU, 4 TOPS)

Power (idle)

150 mW

3 W

5 W

2 W

Power (inference)

1–2 W

5–8 W

10 W

3 W

Connectivity

WiFi, BLE

WiFi, BLE, GbE

GbE, M.2

WiFi, GbE

OS

Linux (Raspbian)

Linux

Linux (Ubuntu)

Linux (Debian)

Typical use

Low-cost edge vision

Prototyping, gateways

Edge vision, robotics

Edge vision, classification

Cost

$15

$35–75

$100–150

$60

Selection notes:

Raspberry Pi Zero 2 W: Cheapest Linux-capable option. Good for prototypes. Limited AI performance (no accelerator).

Coral Dev Board: Best inference performance per watt. Edge TPU accelerates int8 models compiled with Edge TPU compiler.

Jetson Nano: Best for GPU-accelerated vision. CUDA support. Higher power (not battery-friendly).

C.3 Specialized AI SoCs

Spec

Syntiant NDP120

Kendryte K210

Coral Edge TPU (USB)

Core

None (NPU only)

Dual RISC-V @ 400 MHz

N/A (USB accelerator)

AI Accelerator

8-core NPU

KPU (64 MACs)

Edge TPU (4 TOPS)

SRAM

1.5 MB

8 MB

N/A (host device)

Power (active)

200 µW

300 mW

2 W (USB powered)

Power (sleep)

<10 µW

N/A

N/A

Typical use

Always-on voice

Vision (hobbyist)

USB accelerator for Pi/laptop

Supported models

Audio only (keywords, events)

CNN (vision)

TFLite int8 models

Cost

$3–5

$6–8

$60

Selection notes:

Syntiant NDP120: Ultra-low-power audio AI. Cannot run vision or general models. Pairs with host MCU.

K210: Hobbyist favorite. KPU only accelerates convolution—FC layers run on slow RISC-V. Limited commercial support.

Coral USB: Add-on accelerator for desktop/Pi. Not embedded—requires host with USB.

## C.4 Selection Decision Tree

Start Here: What is your primary constraint?

Battery life > 1 year?

 → Use ultra-low-power MCU (STM32L4, nRF52840)

 → Limit: Small models only (<500 KB), infrequent inference

Vision with latency < 100 ms?

 → Use high-performance MCU with NPU (STM32N6) or edge processor (Coral, Jetson)

 → Limit: Higher cost, higher power

Audio (always-on keyword detection)?

 → Use Syntiant NDP120 (ultra-low-power) or ESP32-S3 (WiFi + audio)

 → Limit: Syntiant is audio-only; ESP32 has no FPU

Cost < $5 per unit?

 → Use ESP32-S3, nRF52840, or STM32L4R5

 → Limit: Moderate performance, limited SRAM

WiFi or BLE required?

 → Use ESP32-S3 (WiFi) or nRF52840/nRF5340 (BLE)

 → Limit: Wireless adds power consumption

Linux required (complex software stack)?

 → Use Raspberry Pi or application processor

 → Limit: Higher power (>1 W), not battery-friendly

C.5 Benchmark Performance (Measured Inference Latency)

MobileNetV2-0.35 (96×96 input, int8 quantized)

Hardware

Latency (ms)

Framework

Notes

STM32L4R5 @ 120 MHz

420

TFLite Micro

No SIMD optimization

STM32H7 @ 480 MHz

185

TFLite Micro + CMSIS-NN

Optimized kernels

ESP32-S3 @ 240 MHz

280

TFLite Micro

AI instructions help

nRF52840 @ 64 MHz

650

TFLite Micro

Slow clock, small cache

Raspberry Pi Zero 2 W

45

TFLite (Python)

NEON SIMD

Coral Dev Board (Edge TPU)

8

TFLite + Edge TPU

Hardware acceleration

Takeaway: MCUs: 150–650 ms. Application processors: 10–50 ms. Accelerators: <10 ms.

Keyword Spotting (DS-CNN, 12 layers, 1-second audio)

Hardware

Latency (ms)

Framework

Notes

STM32L4 @ 120 MHz

85

TFLite Micro

Efficient for audio

nRF52840 @ 64 MHz

140

TFLite Micro

Acceptable for 1-second windows

ESP32-S3 @ 240 MHz

60

TFLite Micro

AI instructions help

Syntiant NDP120

2

Proprietary runtime

Specialized NPU

Takeaway: Audio models are smaller than vision. MCUs handle them well. Syntiant is 30–70× faster.

## C.6 Cost vs. Performance Tradeoff

Ultra-Low-Power          Mid-Range              High-Performance

(< $5)                   ($5–$15)               ($15+)

│                        │                      │

nRF52840 ────────────────┼──────────────────────┤

ESP32-S3 ────────────────┼──────────────────────┤

STM32L4R5 ───────────────┼──────────────────────┤

                         STM32H7 ───────────────┤

                         STM32N6 ───────────────┼─────────────

                         nRF5340 ───────────────┤

                                                 Raspberry Pi Zero 2 W ──

                                                 Coral Dev Board ────────

                                                 Jetson Nano ────────────

Performance (MMAC/s):

10–50                    100–400                1000–4000

Rule of thumb:

<$5: 10–50 MMAC/s, good for audio, small vision

$5–$15: 100–400 MMAC/s, good for 96×96 vision, real-time audio

$15+: 1–10 GMAC/s, good for 224×224 vision, real-time video

## C.7 Peripheral and Interface Support

Not all chips support all peripherals. Check before selecting hardware.

Peripheral

STM32H7

ESP32-S3

nRF52840

Raspberry Pi

Camera (parallel)

Yes

Yes

No

Yes (CSI)

Camera (SPI)

Yes

Yes

Yes

Yes

Microphone (I2S/PDM)

Yes

Yes

Yes

Yes (USB)

Accelerometer (I2C/SPI)

Yes

Yes

Yes

Yes

LoRaWAN radio

External SPI

External SPI

External SPI

External SPI

WiFi

External

Integrated

No

Integrated

BLE

External

Integrated

Integrated

Integrated

USB

Yes (OTG)

Yes

Yes

Yes

UART

Yes (8×)

Yes (3×)

Yes (2×)

Yes (2×)

Note: "External" means you add a separate module (e.g., ESP32 WiFi module connected via SPI to STM32). "Integrated" means on-chip.

C.8 Where to Buy and Availability (2024–2025)

Chip Family

Lead Time

Distributors

Dev Boards Available

STM32 (all)

8–20 weeks

Digi-Key, Mouser, Arrow

Yes (Nucleo, Discovery)

nRF52/nRF53

12–16 weeks

Digi-Key, Mouser

Yes (nRF52840 DK)

ESP32

4–8 weeks

Digi-Key, Mouser, direct

Yes (DevKitC)

Raspberry Pi

Stock varies

Adafruit, Sparkfun, direct

N/A (is dev board)

Coral

Stock varies

Google Store, resellers

Yes (Dev Board, USB)

Tip: Lead times fluctuate. Always check distributor stock before committing to a chip in production design.

C.9 Vendor Toolchain and Ecosystem

Vendor

IDE

Compiler

RTOS

TFLite Support

Vendor AI Tools

STMicro

STM32CubeIDE

GCC, ARM CC

FreeRTOS, ThreadX

Yes

STM32Cube.AI

Nordic

nRF Connect SDK

GCC, ARM CC

Zephyr

Yes

Edge Impulse integration

Espressif

ESP-IDF

GCC

FreeRTOS

Yes

ESP-NN (optimized kernels)

Raspberry Pi

Any Linux IDE

GCC

Linux

Yes

N/A (standard TFLite)

Best ecosystem: STM32 (mature tools, large community). ESP32 (excellent docs, active forums). Raspberry Pi (standard Linux).

This hardware reference is a living document. For the latest specs, always consult vendor datasheets and distributor stock. Updated versions of this appendix will be available at the book's companion website.


---

*[<- Appendix B](./appendix-b-ml-quick-reference.md) | [Table of Contents](../README.md) | [Appendix D ->](./appendix-d-toolchain-setup.md)*
