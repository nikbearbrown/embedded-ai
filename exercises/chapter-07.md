## 🛠️ LLM Exercise — Chapter 7: Power and Energy

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** The power verdict module — energy-balance equation, average power, battery-life prediction, and duty-cycle recommendations.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/power.py to the tinyml-feasibility toolkit.

Frozen PowerVerdict dataclass:
- active_energy_mj: float  (energy per inference)
- sleep_power_mw: float
- duty_cycle_s: float  (inference period from app config)
- average_power_mw: float
- battery_life_days: float | None  (None if no battery_mah in app config)
- power_budget_mw: float
- headroom_pct: float
- verdict: Literal["FITS", "TIGHT", "FAILS"]
- mitigations: list[str]
- to_markdown() emits a Power section matching Chapter 14's shape

Public function:
`assess_power(model: ModelSummary, target: Target, app: Application, latency_estimate: LatencyEstimate) -> PowerVerdict`

Implementation:
- active_current_ma = target.active_current_ma_per_mhz * target.clock_mhz
- active_power_mw = active_current_ma * supply_voltage  (default 3.3V; configurable)
- active_energy_mj = active_power_mw * latency_estimate.total_ms / 1000
- sleep_power_mw = target.sleep_current_ua * supply_voltage / 1000
- average_power_mw = (active_energy_mj / duty_cycle_s) + sleep_power_mw
- battery_life_days = (battery_mah * supply_voltage * 3.6 / 1000) / (average_power_mw / 1000) / 86400  (only if app.battery_mah set)
- headroom_pct = (power_budget - average_power) / power_budget * 100
- verdict: FITS if headroom > 20%; FAILS if headroom < 0; TIGHT otherwise
- mitigations:
   - "Increase duty cycle (run inference less often)"
   - "Race-to-sleep — boost clock to finish faster" (recompute and verify it actually wins)
   - "Event-driven trigger (wake on threshold) instead of fixed interval"
   - "Smaller model — less active energy per inference"
   - "Lower-power target — see upgrade_path"

Add `app` fields if missing:
- battery_mah: float | None
- supply_voltage: float (default 3.3)
- duty_cycle_s: float

CLI:
- `tinyml-feasibility check-power --app <yaml> --target <name> --model <path>` prints PowerVerdict including battery_life_days

Tests:
- test_fits_low_duty_cycle — long duty cycle, expect FITS, average power well under budget
- test_fails_continuous_inference — duty_cycle_s=0.01 (continuous), expect FAILS
- test_race_to_sleep_check — for a worked case, faster clock with same model produces lower energy_per_inference
- test_battery_life_calculation — for STM32L4R5 + 1000 mAh + 30s duty cycle + small model, battery_life_days > 365
```

---

**What this produces:** `tinyml-feasibility check-power --app jaguar.yaml --target STM32L4R5 --model jaguar_dscnn.tflite` returns average power, battery life prediction in days, and the verdict with mitigations. This is usually where embedded AI projects find their binding constraint.

**How to adapt this prompt:**
- *For your own project:* The duty_cycle_s field is the most important knob. If verdict fails, scaling the duty cycle is usually cheaper than upgrading hardware.
- *For ChatGPT / Gemini:* Works as-is. Watch for fabricated current numbers — pin to datasheets.
- *For Claude Code:* Best fit.
- *For a Claude Project:* The energy-balance equation generalizes; subsequent chapters (8 accelerator, 9 comms) reuse the same pattern.

**Connection to previous chapters:** Reads ModelSummary (3), Target (2), Application (1), LatencyEstimate (4). Produces the verdict that, combined with chapters 5 and 6, identifies the binding constraint.

**Preview of next chapter:** Chapter 8 adds `accelerator.py` — does adding an NPU close the budget? Cost-benefit calculation against three real candidate targets.
