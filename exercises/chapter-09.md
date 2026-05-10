## 🛠️ LLM Exercise — Chapter 9: Communication: Edge-Cloud

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
- is_feasible: bool  (False if violates a hard constraint like bandwidth ceiling)
- failure_reasons: list[str]

Frozen TierRecommendation dataclass:
- candidate_tiers: list[CommsCost]
- recommended_tier: Literal["cloud", "edge_gateway", "on_device", "hybrid"]
- binding_constraint: str  (e.g., "bandwidth", "energy", "regulation")
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
