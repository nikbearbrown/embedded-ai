# Chapter 9 — Communication and the Edge-Cloud Spectrum

Your model fits in memory, runs in 80 ms, and consumes 12 mJ per inference. All local constraints are satisfied. But the model achieves 87% accuracy, and your application requires 92%. A larger model exists — 2 M parameters, 150 M MACs — that gets to 94%, but it cannot fit on your microcontroller. The device has LoRaWAN connectivity at 1 kbps uplink and 500 ms round-trip to the gateway.

The decision is not whether the cloud is more powerful. Of course it is. The decision is whether the *communication cost* — latency, bandwidth, energy, money, privacy — is acceptable for your application. That decision is what this chapter is about, because most embedded systems live somewhere on a spectrum between fully local processing and fully cloud processing, and the right place on the spectrum is rarely either pole.

Four processing tiers, with different cost profiles. *On-device* (endpoint): inference runs entirely on the device, only the result leaves. Lowest latency (no network involved), best privacy (data never leaves), no connectivity required. Constrained by the device's memory, compute, and power. *Near-edge* (local gateway): a Raspberry Pi or industrial PC in the same building takes raw sensor data over WiFi or Ethernet and runs inference there. Latency 1–50 ms round-trip, plenty of compute, mains-powered. Costs an extra physical box and local infrastructure. *Far-edge* (regional server): inference runs at a regional datacenter or cellular base station. Cellular, LoRaWAN, or satellite link. Latency 50–500 ms and variable, bandwidth limited (1 kbps to 1 Mbps), but compute is essentially unlimited. *Cloud* (centralized datacenter): AWS, Azure, GCP. Latency 100 ms to several seconds depending on network conditions. Recurring bandwidth and compute costs. Infinite scalability, continuous model updates, latest-generation models available.

![Four tier columns side by side — on-device endpoint, near-edge gateway, far-edge regional server, and cloud datacenter — annotated with round-trip latency range, available bandwidth, and compute ceiling. A horizontal axis underneath shows that latency, money, and bandwidth requirements all rise as you move right; a dashed callout marks where data leaves the device.](../images/chapter-09-communication-edge-cloud-fig-01.png)
*Figure 9.1 — Four-tier processing topology. Each tier owns a different cost profile; the design decision is which prefix of the four your application can afford.*

The trade-off surface has four dimensions. *Latency*: on-device is fastest because no network is involved; cloud is slowest because round-trip dominates. Hard real-time applications (collision avoidance, industrial control) cannot tolerate cloud latency. Soft real-time applications (smart home, wearables) often can. *Privacy*: on-device is most private; cloud is least, because raw data crosses the internet and is processed by third parties. Medical devices under HIPAA, security cameras, financial sensors often have regulatory rules that preclude cloud processing entirely. *Connectivity*: on-device requires no network; cloud requires always-on internet. Remote agriculture, wildlife monitoring, maritime, and disaster-response deployments often have no reliable network. *Cost*: on-device has no recurring communication cost but constrained compute. Cloud has recurring bandwidth and API costs but unlimited compute. The economic crossover depends on deployment scale and lifetime.

The decision flow is short. Identify the latency requirement; if it is below 100 ms, you are looking at on-device or near-edge. Identify privacy and regulatory constraints; if data cannot leave the device or facility, cloud is off the table. Identify connectivity availability; if it is not there or it is intermittent, cloud is also off the table. Compare model compute requirements to device capabilities; if the model fits on-device, prefer on-device. If it does not, evaluate offloading by quantifying the four communication costs.

![Vertical flowchart with four diamond gates stacked top to bottom — latency budget under 100 ms, privacy or regulation forbids exfiltration, connectivity intermittent or absent, model fits on device. Each yes arrow goes right to an on-device or near-edge outcome chip; the final no falls into a red-bordered offload box prescribing a four-cost check on latency, bandwidth, energy, and money.](../images/chapter-09-communication-edge-cloud-fig-02.png)
*Figure 9.2 — Tier-selection decision flowchart. The first gate that answers yes wins; only a clean fall-through to the bottom unlocks an offload.*

*Latency cost.* Round-trip time is packetization plus transmission plus propagation plus server queueing and inference plus return transmission plus deserialization. For a LoRaWAN device sending 100 bytes to a server and getting back 10 bytes: serialization 5 ms, LoRa uplink at SF7/125 kHz (effective ~5 kbps) is 100 × 8 / 5,000 = 160 ms, gateway-to-server propagation 50 ms, server inference 20 ms (fast server, small model), LoRa downlink 16 ms, deserialization 2 ms — total round-trip 253 ms. If your application demands 100 ms, the network alone (160 + 50 + 16 = 226 ms) blows the budget before inference begins.

![Horizontal log-scale bar chart of four radio bandwidth ranges from LoRaWAN through WiFi. Three vertical dashed payload markers show the bandwidth each payload needs to clear a 500 ms budget: 96 by 96 RGB image lands inside LTE Cat-M1 and WiFi, 32 by 32 lands inside NB-IoT and above, the 16-element feature vector passes on every radio.](../images/chapter-09-communication-edge-cloud-fig-03.png)
*Figure 9.3 — Radio bandwidth on a log scale, with payload requirements overlaid. A payload fits when its dashed line lands inside the radio's bar.*

*Bandwidth cost.* LoRaWAN is 0.3–50 kbps; NB-IoT 20–250 kbps; LTE Cat-M1 about 1 Mbps; WiFi 1–100 Mbps. A 96 × 96 RGB image is 27,648 bytes. Over LoRaWAN at 5 kbps, transmission is 27,648 × 8 / 5,000 = 44 seconds — useless for real-time. Even WiFi at 1 Mbps takes 0.22 seconds, which is fine for some applications and not for others. The bandwidth check is *(data size / bandwidth) < latency budget*. With a 500 ms budget at 10 kbps, the maximum payload is 0.5 × 10,000 / 8 = 625 bytes. A 96 × 96 image fails. A 32 × 32 image at 3,072 bytes also fails. A 16-element feature vector at 64 bytes passes. This is exactly why edge processing often includes *feature extraction* on-device — instead of sending raw pixels, the device computes a low-dimensional summary (histogram, edge map, statistical moments, learned embedding) and sends that. The bandwidth gap can drop by two or three orders of magnitude.

*Energy cost.* Wireless transmission costs energy proportional to data size and transmission power. A LoRaWAN device transmitting at +14 dBm draws 40 mA; 160 ms of transmission for 100 bytes at SF7 costs 3.3 × 0.04 × 0.16 = 21.1 mJ per transmission. Once every 10 minutes — 144 transmissions a day — gives 3.04 J/day, or 0.013% of a 2,000 mAh / 23,760 J battery per day. Communication energy is negligible at low frequency. But at one transmission every 10 seconds — 8,640 per day — the same per-event cost gives 182 J/day, eight times the entire battery capacity. The battery dies in under three hours. The energy budget for communication is *energy-per-event × events-per-day < average-power-budget × 86,400 seconds*. With a 1 mW budget, you get 86.4 J/day, and at 21 mJ per transmission the maximum sustainable rate is about one transmission every 21 seconds.

![Log-log line chart with seconds between transmissions on the x axis from one second to one day and days of battery life on a 2000 mAh cell on the y axis. Four sloped lines for BLE, LoRaWAN, WiFi, and NB-IoT. A dashed horizontal reference marks the 1 milliwatt average power budget. The collapse zone below 1 day of battery life is called out at the right edge.](../images/chapter-09-communication-edge-cloud-fig-04.png)
*Figure 9.4 — Battery life as a function of transmission interval. Halve the interval, halve the lifetime; halve the per-event energy, double it.*

*Monetary cost.* Cellular plans charge for data. Cloud APIs charge per inference. A device on an NB-IoT $5/month/10 MB plan sending 100 bytes every ten minutes uses 432 KB/month — well inside the plan. Cloud inference at $0.0001 per call, 4,320 calls/month, is $0.43/month. Total per device: $5.43/month. For 10,000 devices: $651,600 a year in operational expense. Compare to running inference on-device with a $5 hardware upgrade: $50,000 upfront, zero recurring. Crossover is under one year. For long-lived deployments, on-device is cheaper. For short-lived deployments or prototypes where the upfront cost dominates, cloud is cheaper. The crossover is application-specific but rarely far away.

Privacy and regulation cut across all four costs and sometimes override them. Medical records under HIPAA and GDPR cannot be transmitted in raw form. Financial transactions are governed by PCI-DSS. Industrial control data may be subject to NIST or IEC standards. Diagnostic medical devices can require FDA or CE clearance, which complicates cloud deployments. The privacy-preserving architecture is to run inference locally and send only the result (label, anomaly flag, summary statistic) to the cloud, storing or discarding raw data on the device. This satisfies most regulatory regimes and most user-trust expectations — *your data never leaves your home*. But it requires the local device to be powerful enough to run the model, which is the hardware constraint Chapter 8 was about.

For some applications, latency requirements alone preclude cloud inference regardless of bandwidth or privacy. Collision avoidance in autonomous vehicles or drones needs detection-to-action under 50 ms; even on a local 5G network with 10 ms RTT, server inference time pushes total latency over the budget. Industrial robotics — pick-and-place, quality inspection — wants 10–100 ms depending on line speed; WiFi RTT plus inference can fit, but jitter blows it. Medical alarms (arrhythmia detection, seizure detection) have one-to-five-second budgets that *theoretically* admit cloud inference but practically fail on reliability — what if the network drops? Voice assistants run at 50–200 ms budgets, which cloud can hit; on-device variants are faster but less accurate. The latency budget determines the maximum allowable network round trip; subtract inference time from the budget, and what is left is the network's share. If it is less than zero, network-based inference is impossible.

*Split inference* is the hybrid pattern that often wins. The model is partitioned: early layers run on the device, later layers run on a server. The device sends *intermediate activations*, not raw data, to the server. Activations are smaller than raw inputs and less interpretable than them, so split inference saves bandwidth and partially preserves privacy. A 96 × 96 image is 27 KB; the activations after three convolutional layers at 24 × 24 × 64 might be 36 KB as float32 or 9 KB as int8 — and the activations look like feature maps, not pictures.

![Horizontal stack of MobileNetV2 layer blocks with heights encoded by activation tensor size — input 150 KB, Conv1 100 KB, Block 3 19 KB, Block 6 8 KB, then Block 10, Block 13, head at 4 KB. A dashed red split-cut line drops between Block 6 and Block 10 separating a device-shaded region from a cloud-shaded region. Bandwidth arrows label 8 KB up and 4 KB down at the cut. A bottom strip compares full on-device 450 ms, split 328 ms, full cloud 1200 ms.](../images/chapter-09-communication-edge-cloud-fig-05.png)
*Figure 9.5 — MobileNetV2 split inference. The split-cut goes where activations are smallest — usually well before the halfway mark of the parameter count.*

Worked example: image classification on an edge camera. MobileNetV2 with 224 × 224 × 3 input (150 KB) runs through Conv1 to 112 × 112 × 32 (100 KB int8), block 3 to 28 × 28 × 96 (19 KB int8), block 6 to 14 × 14 × 160 (8 KB int8), block 13 to 7 × 7 × 320 (4 KB int8), and the final classifier outputs 1,000 classes (4 KB). The split point is the bandwidth check: at 8 KB int8, activations after block 6 fit easily over WiFi. So run blocks 1–6 on the device (about 60% of total operations, 30 M MACs) and blocks 7–13 plus the classification head on the cloud (about 40%, 20 M MACs). Send 8 KB up, get 4 KB back. On an ESP32-S3 with WiFi at 1 Mbps: device inference 180 ms, WiFi up 96 ms, server inference 20 ms, WiFi down 32 ms — 328 ms total. Compare to running the full model on the device at 450 ms (since the ESP32 cannot run the full model efficiently), or full cloud where the raw 150 KB image takes 1,200 ms to upload. Split inference is 1.4× faster than the on-device alternative and 3.7× faster than the full-cloud alternative.

Split works when the device can run part of the model, when activations are smaller than the raw input, and when the latency budget admits a network round trip. It fails when bandwidth is too low even for activations (LoRaWAN at 5 kbps cannot handle 8 KB per inference), when network latency dominates total latency (split is no faster than full cloud), or when privacy demands that no data — not even activations — leaves the device.

*Federated learning* is a separate hybrid pattern that lives at training time rather than inference time. Each device trains locally on its own data, computes weight updates (gradients or deltas), and sends only the updates to a central server. The server aggregates across thousands of devices and sends an improved model back. Raw data never leaves the devices, which solves privacy. The bandwidth cost shifts to weight updates (megabytes once per training round) instead of raw training data (gigabytes). Federated learning matters for embedded AI when you have many deployed devices generating data continuously, you want the model to keep improving from that data, and privacy or bandwidth rules out shipping raw data centrally. It is not a free lunch — it requires devices to do *training*, not just inference, which is a much higher hardware bar than this book's main subject.

To make the spectrum concrete, work a deployment. Predictive maintenance for industrial motors. Three candidate models: small (50,000 params, 8 M MACs, 82% accuracy), medium (200,000 params, 40 M MACs, 91%), large (1 M params, 200 M MACs, 96%). Application: ≥90% accuracy required, ≤1 second latency (soft), NB-IoT connectivity at 20 kbps and 200 ms RTT, data is proprietary but not regulated (cloud is allowed), <$10/device/month for communication and compute.

Strategy 1, full on-device, Model B: STM32H7 at 480 MHz runs Model B in 220 ms. Send the 1-byte fault prediction once a day. Monthly data: 30 bytes. Monthly cost: $2 minimum NB-IoT plan. 91% accuracy. All constraints met, accuracy at the floor.

Strategy 2, full cloud, Model C: low-power STM32L4 just for sensor acquisition. Send 1 kHz accelerometer over 60-second windows = 180 KB per transmission. Hourly transmissions = 24/day. Monthly data: 129.6 MB. NB-IoT plan needs 200 MB at $25/month. Cloud inference $0.72/month. Total $25.72/month. 250 ms latency, 96% accuracy. Cost is 2.6× over budget; bandwidth is the dominating cost. Unviable on cost.

Strategy 3, split inference, Model C with first five layers on the device: STM32H7 again. First five layers locally — 30 M MACs, 120 ms. Activation after layer 5: 4 KB int8. Send that, get back the result. Hourly transmissions = 24/day. Monthly data: 4 KB × 24 × 30 = 2.88 MB. NB-IoT $5/month/10 MB plan. Cloud inference $0.72/month. Total $5.72/month. Latency: 120 + 200 + 30 = 350 ms, comfortably inside the 1-second budget. Accuracy 96% (Model C in full).

Strategy 3 wins. Same accuracy as full cloud, 4.5× cheaper, well within latency. 45× lower bandwidth than the full cloud option. The split point — between the layers that fit on the device and the layers that do not — is the design lever, and it is the lever the on-device-versus-cloud framing of this question hides. *The edge-cloud decision is not binary, and hybrid strategies usually beat either pole.*

![Four small bar panels arranged two by two — latency in milliseconds, monthly data in megabytes, monthly cost in dollars, and accuracy percent — each showing three bars for Strategy 1 on-device, Strategy 2 full cloud, and Strategy 3 split inference. Each panel carries a budget reference line. Strategy 2 is labeled over budget on the cost panel; Strategy 3 is labeled the winner on the accuracy panel.](../images/chapter-09-communication-edge-cloud-fig-06.png)
*Figure 9.6 — Three predictive-maintenance strategies on four axes. Split inference matches Model C accuracy at 4.5× lower monthly cost, well inside the 1 s latency budget.*

There are deployments where communication has to be rejected entirely. Underwater sensors, remote agriculture, disaster-response robots — the network is absent most of the time. Medical implants and industrial safety systems — network failures cannot be tolerated, period. Military and security applications where the network may be jammed or compromised. For these, on-device inference is not an optimization. It is the requirement. The model has to fit on the device, even at the cost of accuracy or upgraded hardware.

The next chapter takes the hardest constraint category: real-time guarantees. The edge-cloud spectrum assumed inference completes in a timely, predictable manner. When inference has to meet hard deadlines with provable certainty, neural networks become genuinely difficult to integrate into safety-critical systems, and the patterns that reduce risk are worth knowing in detail.

---

## LLM Exercise — Chapter 9: Communication: Edge-Cloud

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** A communication-cost calculator that scores each processing tier (cloud / edge gateway / on-device / hybrid) on the four communication costs and recommends the right tier for the application.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/comms.py to the tinyml-feasibility toolkit.

Frozen CommsCost dataclass:
- tier: Literal["cloud", "edge_gateway", "on_device", "hybrid"]
- payload_size_bytes: int
- frequency_per_day: float
- latency_round_trip_ms: int
- bandwidth_required_kbps: float
- energy_per_message_mj: float
- monthly_cost_usd: float
- is_feasible: bool (False if violates a hard constraint like bandwidth ceiling)
- failure_reasons: list[str]

Frozen TierRecommendation dataclass:
- candidate_tiers: list[CommsCost]
- recommended_tier: Literal["cloud", "edge_gateway", "on_device", "hybrid"]
- binding_constraint: str (e.g., "bandwidth", "energy", "regulation")
- justification: str
- to_markdown() emits a Communication section matching Chapter 14's shape

Public functions:
- `assess_comms(app: Application, model: ModelSummary, target: Target) -> TierRecommendation`
- Use a RADIO_PROFILES dict mapping radio names ("LoRaWAN", "NB-IoT", "WiFi", "BLE", "Cellular-LTE-M") to (max_bandwidth_kbps, energy_per_byte_mj, monthly_cost_usd_per_device, regulatory_duty_cycle_pct). Cite each entry with a datasheet/spec URL in a comment.

Implementation:
- For "cloud" tier: payload_size = raw_input_size (e.g., 224*224*3 for image, 16000 audio samples for KWS)
- For "edge_gateway" tier: payload_size = compressed input (JPEG for image, opus for audio)
- For "on_device" tier: payload_size = classification result only (~10 bytes)
- For "hybrid" tier: payload_size = on_device size most of the time, cloud size occasionally (configurable threshold)
- For each tier, compute round-trip latency, required bandwidth, energy per message, monthly cost
- is_feasible = False if required_bandwidth > radio max OR if app forbids cloud (privacy/HIPAA flag)
- recommended_tier: cheapest feasible tier that also meets app.latency_budget_ms

CLI:
- `tinyml-feasibility check-comms --app <yaml> --target <name> --model <path> --radio LoRaWAN` prints TierRecommendation

Tests:
- test_lorawan_forbids_cloud_for_images — image classifier + LoRaWAN, expect cloud tier infeasible (bandwidth)
- test_wifi_makes_cloud_feasible — same model + WiFi, expect cloud tier feasible
- test_hipaa_forbids_cloud — app.privacy_class="HIPAA", expect cloud and gateway both infeasible
```

---

**What this produces:** `tinyml-feasibility check-comms --app vineyard.yaml --target RPi-Zero-2W --model efficientnet-lite0.tflite --radio LoRaWAN` directly replicates Chapter 14's vineyard arithmetic — finds that cloud is physically infeasible on LoRaWAN and recommends on-device.

**How to adapt this prompt:**
- *For your own project:* The RADIO_PROFILES dict is where most of the per-deployment-context lives. Add your radio with real datasheet citations.
- *For ChatGPT / Gemini:* Works as-is.
- *For Claude Code:* Use `--allowed-tools edit,bash,web_search` for radio spec lookups.
- *For a Claude Project:* Pin RADIO_PROFILES to the system prompt — it's heavy reference data subsequent modules read.

**Connection to previous chapters:** Reads ModelSummary, Target, and Application. Produces the architectural decision (which tier) that frames whether downstream optimization (chapters 11, 12) needs to happen at all.

**Preview of next chapter:** Chapter 10 adds `realtime.py` — assess WCET against deadline, identify safety-class implications, recommend a design pattern (advisory / bounded / confidence-gating / voting / hierarchical) for AI in safety-critical loops.

---

## Prompts

Use these prompts with Claude to generate interactive D3 v7 versions of the figures in this chapter. Each produces a standalone HTML file you can open in a browser and modify freely.

**Prerequisites:** Load `brutalist/CLAUDE.md` and `brutalist/DESIGN.md` into your Claude project context before using these prompts. They define the stack, naming conventions, color system, and typography the figures use.

---

### Figure 9.1 — Four-tier processing topology

Build a four-column comparison figure rendering the processing tiers a sensor reading can traverse. Columns left to right: on-device endpoint MCU, near-edge local gateway, far-edge regional server, cloud datacenter. Each column is a card with a header strip in increasing luminance, a tier name, and three monospace spec rows — round-trip latency, available uplink bandwidth, and compute ceiling — followed by a strength line, a limit line, and one named example. Below the cards, render a horizontal axis with an arrowhead and labels "fast · private · constrained" on the left and "scalable · costly · always-online" on the right, then "latency · money · bandwidth ceiling →" centered. Place a red-dashed callout box under the far-edge and cloud columns naming HIPAA, GDPR, PCI-DSS. Hovering a card dims the other three and shows a tooltip with the full cost profile. Standalone HTML, D3 v7 7.9.0 from the cdnjs URL, EB Garamond / Inter / JetBrains Mono Google Fonts, dark-mode aware, ResizeObserver redraw, accessible.

> Reference implementation: `d3/chapter-09-communication-edge-cloud-fig-01.html`

---

### Figure 9.2 — Tier-selection decision flowchart

Build a vertical decision flowchart with four diamond gates stacked top to bottom: (1) latency budget < 100 ms? (2) privacy or regulation forbids exfiltration? (3) connectivity intermittent or absent? (4) model fits on device? Each gate carries a bold question on the first line and an italic example list on the second. From each gate, a YES arrow exits right to a black outcome chip — gate 1 reads "on-device or near-edge," gates 2 and 3 read "on-device only," gate 4 reads "prefer on-device." NO arrows continue down the spine to the next gate. Below the last gate, a red-bordered offload box reads "run the four-cost check: latency, bandwidth, energy, money." Hovering a gate shows a tooltip explaining the constraint in one sentence. Standalone HTML, D3 v7, dark-mode aware, ResizeObserver redraw, accessible. Use `var(--color-*)` only; no hardcoded hex.

> Reference implementation: `d3/chapter-09-communication-edge-cloud-fig-02.html`

---

### Figure 9.3 — Radio bandwidth ranges with payload markers

Build a horizontal log-scale chart showing four radio uplink bandwidth ranges as solid bars: LoRaWAN 0.3–50 kbps, NB-IoT 20–250 kbps, LTE Cat-M1 50–1 000 kbps, WiFi 1 000–100 000 kbps. The x-axis is bandwidth on a log scale from 0.1 kbps to 100 000 kbps. Overlay three vertical dashed payload markers showing the bandwidth each payload requires to clear a 500 ms budget — 96×96 RGB image (27 KB → 442 kbps), 32×32 RGB image (3 KB → 49 kbps), 16-element feature vector (64 B → 1 kbps). Bars use a luminance sequence: LoRaWAN var(--color-ink), NB-IoT var(--color-secondary), LTE Cat-M1 #787878, WiFi var(--color-border). Failing-payload markers in var(--color-red); passing marker in var(--color-ink). Hovering a radio bar dims the other three. Standalone HTML, D3 v7, dark-mode aware, accessible, ResizeObserver redraw.

> Reference implementation: `d3/chapter-09-communication-edge-cloud-fig-03.html`

---

### Figure 9.4 — Battery life vs transmission interval

Build a log-log line chart with seconds between transmissions on the x-axis (1 s to 86 400 s) and days of battery life on a 2 000 mAh × 3.3 V cell on the y-axis (0.1 d to 10 000 d, clamped). Four lines: BLE 0.1 mJ/event (dashed var(--color-secondary)), LoRaWAN 21 mJ/event (var(--color-ink)), WiFi 50 mJ/event (#787878), NB-IoT 150 mJ/event (var(--color-red)). Compute days from cellJoules × T / (86 400 × mJ/1 000). Add a dashed horizontal reference line for the 1 mW average-power budget (≈ 275 days). Right-side legend with line swatch, radio name, and a one-line transmit-burst note. Annotate the upper-left region "years on a coin cell" and the lower-right region "hours, not days" in italic EB Garamond. Hovering a line dims the others and shows lifetime at 1 min and 1 hr intervals. Standalone HTML, D3 v7, dark-mode aware, accessible, ResizeObserver redraw.

> Reference implementation: `d3/chapter-09-communication-edge-cloud-fig-04.html`

---

### Figure 9.5 — MobileNetV2 split-inference diagram

Build a horizontal layer-block diagram for MobileNetV2 with 224×224×3 input. Seven blocks across: Input (150 KB), Conv1 (100 KB), Block 3 (19 KB), Block 6 (8 KB · split cut), Block 10 (6 KB), Block 13 (4 KB), Head (4 KB). Encode activation size as rectangle height with `d3.scaleSqrt()`. Top edge has a two-tone strip: dark var(--color-ink) "DEVICE — ESP32-S3 · blocks 1 to 6 · 30 M MACs · 180 ms" over the device blocks, var(--color-secondary) "CLOUD — server · blocks 7 to 13 + head · 20 M MACs · 20 ms" over the cloud blocks. A red dashed vertical split-cut between Block 6 and Block 10 with labels "split cut", "↑ 8 KB up · ↓ 4 KB down", "96 ms at 1 Mbps WiFi". Below the blocks, a horizontal comparison strip with three bars proportional to ms: FULL ON-DEVICE 450 ms, SPLIT 328 ms, FULL CLOUD 1 200 ms, each annotated. Hover a block to dim the others and show shape/size tooltip. Standalone HTML, D3 v7, dark-mode aware, accessible, ResizeObserver redraw.

> Reference implementation: `d3/chapter-09-communication-edge-cloud-fig-05.html`

---

### Figure 9.6 — Three strategies on four axes

Build a 2×2 grid of small bar panels comparing three predictive-maintenance strategies on independent axes: (top-left) Latency ms, budget 1 000 ms; (top-right) Monthly data MB, 10 MB plan ceiling; (bottom-left) Monthly cost $, ≤ $10/mo; (bottom-right) Accuracy %, floor 90 %. Each panel: three bars for S1 (on-device, #787878), S2 (full cloud, var(--color-border)), S3 (split, var(--color-ink)). Values: latency 220/250/350; data 0.00003/129.6/2.88; cost $2.00/$25.72/$5.72; accuracy 91/96/96. Each panel carries a red dashed budget reference line and a label in the top-right corner — "S2 over budget" in red on the cost panel, "S3 wins" as a black chip on the accuracy panel. Bar value labels above each bar in formatted units. Hover for tooltip; tabindex 0; aria-label per bar. Standalone HTML, D3 v7, dark-mode aware, accessible, ResizeObserver redraw.

> Reference implementation: `d3/chapter-09-communication-edge-cloud-fig-06.html`

---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Radia Perlman** designed the spanning tree protocol that makes every Ethernet network work — the kind of distributed coordination that decides where your edge inference output ends up.

**Run this:**

```
Who was Radia Perlman, and how does her work on the spanning tree protocol and network design connect to today's edge-cloud architectures and split inference? Three paragraphs. End with the single most surprising thing about her career.
```

→ Search **"Radia Perlman"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain spanning tree protocol in plain language, with one example
- Ask it to compare Perlman's design priorities to what an edge-cloud ML system has to coordinate today
- Add a constraint: "Answer in the form of a poem about networks (Perlman wrote one about her own protocol)"

What changes? What gets better? What gets worse?
