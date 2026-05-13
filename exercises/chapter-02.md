## LLM Exercise — Chapter 2: Embedded Constraints as Design Variables

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** A `Target` dataclass with a real microcontroller catalog, and a `Constraints` translator that converts `Application` + `Target` into the four-constraint object the toolkit reasons over.
**Tool:** Claude Code

---

**The Prompt:**

```
Extend the tinyml-feasibility package (chapter 1 set up the scaffold and Application).

Add two modules:

1. src/tinyml_feasibility/target.py
 Frozen Target dataclass with fields: name, core (e.g., "Cortex-M4"), clock_mhz, sram_kb, flash_kb, active_current_ma_per_mhz, sleep_current_ua, has_accelerator (bool), accelerator_tops (float, 0.0 if none), cost_usd.
 Provide a TARGETS dict mapping name → Target instance, populated from datasheets for at least: STM32L4R5, STM32H743, STM32N6, nRF52840, ESP32-S3, RPi-Zero-2W, Arduino-Nano-33-BLE-Sense.
 Every numeric value gets a comment with the datasheet URL it came from. NO FABRICATION — if a number can't be sourced, leave it None and emit a warning.

2. src/tinyml_feasibility/constraints.py
 Constraint dataclass: category (Literal["memory","compute","power","real_time"]), axis (str, e.g., "sram_kb", "latency_ms"), budget (float | str), source (str pointing to where the budget came from, e.g., "application.memory_budget.sram_kb").
 Function `derive_constraints(app: Application, target: Target) -> list[Constraint]` produces one Constraint per axis: memory:flash, memory:sram, compute:latency, power:average, real_time:class.

CLI extension:
- `tinyml-feasibility list-targets` prints each Target as a table (name, core, clock, sram, flash, sleep current, cost)
- `tinyml-feasibility constraints --app <yaml> --target <name>` prints the derived Constraint list with sources

Tests:
- test_target_lookup — TARGETS["STM32L4R5"] returns a Target with sleep_current_ua < 1.0
- test_constraints_derived — for the example app + STM32L4R5, derive_constraints returns exactly 5 Constraint instances covering all four categories
- test_constraints_traceable — every Constraint.source is a non-empty string

Run pytest. All tests pass before you stop.
```

---

**What this produces:** A microcontroller catalog (with traceable datasheet citations) and a translator that turns application requirements + target into the structured Constraint list the toolkit will use everywhere downstream.

**How to adapt this prompt:**
- *For your own project:* Add your target board to TARGETS by reading its datasheet. Note Claude is good at extracting datasheet numbers but verify each one against the source PDF before committing.
- *For ChatGPT / Gemini:* Works as-is.
- *For Claude Code:* Use `--allowed-tools edit,bash,web_search` so it can pull datasheet values. Always sanity-check the citations before merging.
- *For a Claude Project:* Add the Target dataclass schema to the system prompt; this saves chapters 5–10 from re-deriving it.

**Connection to previous chapters:** Chapter 1's `Application` is now consumed alongside `Target` by `derive_constraints`. The four-constraint object becomes the contract every later module reads.

**Preview of next chapter:** Chapter 3 adds `model.py` to load a TFLite model file and extract parameter count, MAC count, layer types, and the largest activation tensor — the inputs every memory/compute/power module will need.
