# Chapter 14 — Integration Case Studies: Full Design Decisions

A precision-agriculture company wants to detect grape diseases in vineyards seven to ten days before symptoms appear, so growers can spray a single vine instead of an entire block. The plan is straightforward in outline: solar-powered sensors take pictures of leaves, an image classifier identifies powdery mildew and downy mildew, and the result goes home over LoRaWAN.

The plan dies on a single arithmetic check. A 224×224 RGB image is 150 KB raw. Compressed to a JPEG it's around 20 KB. LoRaWAN's payload at the lowest spreading factor caps around 50 kbps and at the longest range delivers maybe 1 kbps; either way, transmitting one 20 KB image takes between three and five minutes, and the duty-cycle limits in the regulatory band restrict you to about 30 seconds of airtime per hour per device. Cloud processing, the architecture that worked for every other ML product the team has shipped, is *physically impossible* on this radio. The image must be classified before transmission. On-device inference is not the cheap design choice — it is the only design that fits the bandwidth budget.

This is what the framework does. Constraints — power, memory, latency, bandwidth, cost, regulatory — narrow the design space until usually one or two architectures survive. The same framework, applied to three different problems with three different binding constraints, produces three completely different deployments. That is the point of this chapter. You have learned the moves separately. Here are three problems where every move runs at once.

## Industrial vibration monitoring — when power is the binding constraint

Two hundred CNC milling machines, run continuously. A bearing failure costs $50,000 in repair and $10,000 per hour of downtime. The proposal: a vibration sensor on each machine that flags imminent failures 24–48 hours in advance so maintenance can be scheduled instead of called.

The acceptance specs land at ≥95% sensitivity, <5% false-positive rate, detection within 10 seconds (soft real-time), and an 18-month battery life on a coin-cell-class power source. Cost ceiling $40 per sensor. No cloud connectivity — the factory has no Wi-Fi and cellular at $5 per device per month against 200 devices breaks the operating-cost budget.

Eighteen months on a 1,000 mAh Li-ion cell at 3.7 V is 13,320 J of total energy. Spread across the deployment lifetime, that's 0.28 mW of average power. Sleep current alone at 10 µA is 0.037 mW — already 13% of the budget. Inference must be very fast or very rare.

Three architectures get considered. Fully on-device, with results stored locally and transmitted once a day to a wired gateway. An edge-gateway architecture with raw vibration streaming to an industrial PC over RS-485. And a hybrid where a simple threshold on the device wakes a radio and forwards a one-second window to the gateway for ML classification.

On-device wins. The gateway architecture demands wiring 200 sensors, which exceeds the deployment budget. The hybrid demands a sub-GHz radio per sensor, which exceeds the BOM. The challenge is putting all the ML on a microcontroller and still hitting the 18-month battery target.

The model decision then collapses. A 1D CNN on raw vibration is too expensive in memory and power for the duty cycle the energy budget allows. An autoencoder is hard to threshold reliably. A threshold-only detector tops out around 70% sensitivity, well below requirement. A random forest on engineered vibration features (RMS, spectral peaks, kurtosis, zero-crossing rate, harmonic ratios, FFT dominant frequencies — 25 features in the second iteration) gets to 94% sensitivity at 4% false-positive rate, fits in 200 KB of flash, and runs in 5 ms.

Hardware: STM32L4R5 at 120 MHz, 640 KB SRAM, 2 MB flash, 0.4 µA sleep current. Sleep current is the deciding number. The nRF52840 sits at 2.8 µA, the ESP32-S3 at 10 µA. Multiplied across 18 months those differences crater the battery life. At $6 the L4R5 leaves $34 for the accelerometer, enclosure, battery, and PCB.

The inference schedule comes out of an energy-balance equation. Each inference burns about 0.66 mJ — 0.44 mJ for feature extraction plus 0.22 mJ for the random forest evaluation. Sleep dissipates 0.00148 mW continuously. Setting the average against the 0.28 mW budget gives an inference interval of about 2.4 seconds. The system runs inference every 2.5 seconds, which provides 1,500 detection opportunities per hour against degradation that develops over hours to days.

Field trial across five units for one month. Battery extrapolation: 16.5 months — short of the 18-month target by about 8%, livable. Sensitivity 91% on three actual faults observed (small sample). False-positive rate 8%, almost double the validation number. Root cause: vibration from adjacent machines triggering false alarms. Firmware fix: spatial filtering — if only one sensor in a cluster triggers, treat it as suspect. False-positive rate drops to 4.5%. Final BOM: $38 per unit. Sensitivity below the 95% target but accepted by the product team given the cost constraints.

What rejection looks like here: a 1D CNN model would have been more accurate, but it would have demanded a larger battery, which would have broken the cost ceiling. The constraint that drove every decision was the milliwatt-scale energy budget; everything else followed.

## Medical wearable — when accuracy and regulation are binding

A wearable single-lead ECG monitor for outpatient cardiac-rhythm monitoring. Five arrhythmia classes including ventricular tachycardia and ventricular fibrillation. Sensitivity ≥98% for the life-threatening classes is the regulatory floor — ventricular tachycardia missed is a person who dies. Specificity ≥95%. Alert latency within 30 seconds. FDA Class II, 510(k) pathway, IEC 62304 software-lifecycle compliance, cybersecurity documentation, clinical validation against board-certified cardiologist annotations.

Seven days of battery life on a 500 mAh Li-ion cell at 3.7 V — 6,660 J — gives an average power budget of 11 mW. Tight, but fifty times more generous than the industrial case. The constraint that bites is not power. It is accuracy under regulatory scrutiny.

Architecture choice closes immediately. Streaming raw ECG to a paired smartphone and processing there violates HIPAA in spirit and complicates the FDA submission — the smartphone becomes part of the medical device. Hybrid screening with smartphone confirmation has a connectivity dependency the regulator will not bless. Fully on-device: deterministic, no connectivity dependency, raw ECG never leaves the wearable, the algorithm is the device.

Model selection runs into the regulatory floor. Rule-based detectors, the way Holter monitors work, top out around 92% sensitivity in published studies — not enough for VT/VF. LSTMs on RR intervals depend on QRS detection quality, which fails on noisy ECG. Hybrid CNN-plus-classifier sits at 95–97%, just shy. Only a 1D CNN on raw ECG hits 98%+ sensitivity for VT/VF in the literature.

The state-of-the-art ResNet-flavored 1D CNN comes in at 18 layers, 2.5 million parameters, 10 MB at float32. The wearable SoC has 2 MB of flash and 512 KB of SRAM. The compression sequence runs as the previous chapter prescribed: prune first, distill second, quantize last. Forty percent structured pruning brings the parameter count to 1.5 million and recovers VT/VF sensitivity to 97.2% after fine-tuning — below threshold. Distillation onto a smaller 8-layer student against the pruned teacher: 800,000 parameters, sensitivity back up to 98.1%. QAT to int8: 800 KB of weights, 180 KB of activations, sensitivity 97.8%. The post-quantization number sits 0.2 percentage points below the 98% acceptance bar; the product team accepts the gap with a plan to close it through post-market data and updates.

Hardware: STM32U5 at 160 MHz, 2 MB flash, 786 KB SRAM, TrustZone for secure boot and signed firmware updates. Three dollars more expensive than the nRF5340 alternative, and the TrustZone is exactly what the FDA cybersecurity guidance asks for in a connected medical device. Total BOM $180 inside the $200 ceiling.

Inference scheduling exploits the soft latency. ECG samples at 250 Hz; arrhythmia detection looks at 10-second windows. Inference takes 120 ms on the U5. The duty cycle is 1.2% — 120 ms of compute every 10 seconds. Energy per cycle: 11.1 mJ for the inference, 37 mJ for continuous ECG acquisition, 0.18 mJ for processor sleep. Average power 4.85 mW against an 11 mW budget. Battery-life calculation gives 16 days of pure inference and acquisition; Bluetooth alerts and display updates eat the rest, target 7 days is met.

Validation is the part most embedded ML projects underestimate. 510(k) requires clinical data: 500 patients, diverse demographics, board-certified cardiologist annotations as ground truth, model sensitivity and specificity measured against that ground truth. Eighteen months from prototype to clearance. Field accuracy will not match validation accuracy until that data set is built.

What rejection looks like here: smartphone processing was rejected on regulatory grounds, not technical ones — the algorithm could have run there with more compute and a larger battery, but the device classification and HIPAA exposure cost more than the technical wins paid for. Cost was a soft constraint, accuracy was a hard one, and regulation determined the architecture.

## Agricultural disease detection — when bandwidth and harvesting are binding

Back to the vineyard. Solar panel 2 W peak, averaging 0.5 W across a 24-hour day after night, clouds, and angle losses. A 5,000 mAh Li-ion buffer battery — 18.5 Wh, 66,600 J — to ride out overcast stretches. LoRaWAN as the only radio. Cost ceiling $150. Three classes: healthy, powdery mildew, downy mildew. Accuracy threshold 85%.

Bandwidth, not power, is the binding constraint. Solar harvesting gives a generous 500 mW average; LoRaWAN gives 1–50 kbps and a regulatory duty-cycle ceiling. Cloud inference would mean transmitting one image every six hours — physically incompatible with the radio. Edge-gateway architectures with a Raspberry Pi running per vineyard would work technically, but they add $200–300 per vineyard in gateway hardware and create a single point of failure across 20–50 sensors. Fully on-device wins: classify locally, transmit ten bytes (timestamp, class, confidence) instead of twenty kilobytes.

Model selection hinges on what fits inside an SoC that can also run a camera and a LoRaWAN modem under 500 mW average. MobileNetV2-1.0 is too large. MobileNetV2-0.35 fits but tops out around 82% accuracy on agricultural datasets — below threshold. A custom lightweight CNN runs out of capacity for distinguishing early-stage symptoms. EfficientNet-Lite0 at 4.6 MB int8 with 350–500 ms inference lands at 88–92% on similar tasks. It clears the threshold with margin and fits the duty-cycle envelope.

Hardware: Raspberry Pi Zero 2 W. The ESP32-S3 alternative is cheaper and lower-power but its 512 KB of SRAM cannot hold the activations for a 224×224 input through EfficientNet's depth. The STM32H7 lacks on-chip flash for the model and SRAM for the activations. The Pi Zero burns 1–2 W during inference, but at four inferences per day at two seconds each, total inference energy is 12 Wh per day; sleep at 150 mW for the rest of the day adds 3.6 Wh; total 15.6 Wh against a worst-case 12 Wh of solar plus an 18.5 Wh battery buffer. The buffer covers about 1.5 days of full overcast — enough.

Inference scheduling is event-driven by daylight. A photoresistor wakes the system at sunrise; captures and inferences run at 7 AM (after dew evaporates — the field trial taught us this), 10 AM, 2 PM, and 6 PM. Each event burns about 4.3 J. Daily total around 12,900 J including sleep. Energy balance positive on average; battery covers the variance.

Training: 5,000 grape-leaf images split across the three classes, captured in actual vineyards across the growing season. EfficientNet-Lite0 fine-tuned from ImageNet weights. Validation accuracy 91.2% at float32, 89.8% int8 PTQ — both above threshold. Deployment via TFLite for Python, picamera, pyLoRa, cron-driven scheduling.

Field trial across ten sensors in two vineyards for three months. On-device accuracy 87.3% — lower than the validation number because field images carry more variation than training data. Eight percent false negatives, five percent false positives. Battery life indefinite through the trial including a five-consecutive-day overcast stretch. Two issues found: morning dew degraded accuracy (fixed by shifting first capture to 7 AM); LoRaWAN coverage gaps required one repeater per vineyard.

What rejection looks like here: cloud processing was eliminated by physics, not preference. The bandwidth-multiplied-by-airtime budget cannot move 20 KB images at 6-hour intervals. Every other architectural choice was downstream of that one constraint.

## What the three cases share

The framework was the same in all three. Quantify constraints. Choose the processing architecture. Choose the model class. Choose the hardware. Optimize the model. Schedule inference inside the energy budget. Validate on target. Document the rejected alternatives and the constraints that killed them.

The outputs differ because the *binding* constraint differs. In the industrial case it was power — 0.28 mW average across 18 months drove the hardware choice (lowest sleep current), the model choice (random forest, not CNN), and the inference schedule (every 2.5 seconds, no faster). In the medical case it was the regulatory floor on sensitivity — 98% for VT/VF drove the model class (1D CNN on raw ECG, not anything cheaper), the optimization sequence (aggressive pruning followed by distillation followed by QAT), and even the hardware (TrustZone for FDA cybersecurity expectations). In the agricultural case it was bandwidth — LoRaWAN's data rate forced on-device inference, which forced a model that fits, which forced an SoC big enough to run it, which forced a solar-and-buffer power architecture to support that SoC.

There is no universal answer to "should this run on-device or in the cloud" or "which model architecture should we use." There are only constraints and the architectures those constraints permit. The framework's job is not to produce a recommendation. It is to make the binding constraint visible early, so that the architecture which survives is the one the application actually permits, not the one the team is most comfortable building.

What would change my mind: if a survey of deployed embedded AI systems showed that the binding constraint at design time often wasn't the binding constraint at production scale — if power-budgeted designs routinely fell on bandwidth or thermal limits in deployment, for instance — that would tell me the framework's "find the binding constraint" move is too clean for how these projects actually break.

Still puzzling: how to choose between two viable architectures when their binding constraints are different ones at the *same level of tightness* — when on-device just barely fits the power budget and edge-gateway just barely fits the bandwidth budget, and either could be made to work with effort. The framework lets you eliminate infeasible options. It does not give you a sharp answer for choosing between feasible ones with different residual risks.

---

## LLM Exercise — Chapter 14: Integration Case Studies — Full Design Decisions

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
- rejected_alternatives: list[dict] (each: name, reason, citation back to verdict)
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

---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **W. Ross Ashby** was a British psychiatrist who founded cybernetics from the inside out, and his Law of Requisite Variety — a controller must have at least as much variety as the system it controls — is the structural reason why constraints decide your architecture, not your preferences.

**Run this:**

```
Who was W. Ross Ashby, and how does his Law of Requisite Variety connect to the way embedded AI architectures get forced by their binding constraints? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"W. Ross Ashby"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain the Law of Requisite Variety in plain language, with one example
- Ask it to compare Ashby's idea to the case-study finding that the binding constraint determines the deployment architecture
- Add a constraint: "Answer as if you're writing the closing paragraph of a systems-design textbook"

What changes? What gets better? What gets worse?
