# Chapter 7 — Power and Energy

Three weeks after a wildlife monitoring camera goes into the field, the batteries die. The unit was specified for six months on four AA cells, running inference every 30 seconds and transmitting once an hour. There is no fault report, no crash, no error. Classifications are correct. The unit just runs out of power 22 times faster than calculated.

You retrieve a unit and profile it. Measured current during inference: 85 mA. Predicted: 40 mA. The model runs correctly and consumes twice the predicted power, and at the duty cycle the system is running, twice the predicted power means the battery that should have lasted 4,380 hours lasts 200.

This is the power constraint, and it is unlike the memory and compute constraints in an important way: when memory or compute fails, the system fails loudly — crashes, missed deadlines, errors you can debug from a stack trace. When power fails, the system *succeeds quietly* until the battery dies. Every measurement is right, every classification is right, and the deployment is dead anyway. For battery-powered or energy-harvesting devices, power is usually the binding constraint. The memory and the compute can both be satisfied and the deployment still fails on this one.

Begin with a distinction that confuses people. *Power* is the instantaneous rate of energy consumption, measured in watts. A device drawing 50 mW consumes 50 millijoules every second. *Energy* is the total quantity, measured in joules or watt-hours: 50 mW for 10 seconds is 0.5 J. *Energy = Power × Time.* For battery-powered systems, what determines battery life is total energy consumed, not the instantaneous power — unless instantaneous power exceeds what the supply can deliver, which is the separate peak-power constraint from Chapter 2. A 1,000 mAh lithium-ion cell at 3.7 V stores 3.7 Wh = 13,320 J. At an average draw of 10 mW, that is 13,320 / 0.01 = 1,332,000 seconds, or about 15 days.

Now: that 10 mW average can come from running steadily at 10 mW, or from running at 200 mW for 5% of the time and at 0.5 mW for 95% of the time:

$$
P_{\text{avg}} = (200 \times 0.05) + (0.5 \times 0.95) = 10 + 0.475 = 10.475\ \text{mW}.
$$

Battery life is essentially the same because average power is essentially the same. *Duty cycling* — running at high power for short bursts and sleeping at low power between them — is the entire reason embedded AI is feasible on coin cells.

![Two current-vs-time traces over the same 10-second window. The left panel shows a steady 10 mW draw as a flat line; the right shows tall narrow 200 mW spikes at 5% duty rising from a 0.5 mW sleep floor. Both have the same area under the curve, and therefore the same average power.](../images/chapter-07-power-and-energy-fig-01.png)
*Figure 7.1 — Same average power, two current profiles. Battery life is set by area under the curve, not peak height.*

The mistake the doorbell team in Chapter 1 and the wildlife-camera team in this chapter both made is calculating power from the active current alone. A model that runs at 60 mA for 80 ms every 10 seconds does not consume 60 mA on average. With sleep current at 5 µA, average current is

$$
I_{\text{avg}} = \frac{60\ \text{mA} \cdot 0.08\ \text{s} + 0.005\ \text{mA} \cdot 9.92\ \text{s}}{10\ \text{s}} = 0.53\ \text{mA},
$$

which is roughly 100× lower than the active current. Sleep current dominates average power when the duty cycle is low, and most embedded AI systems run at very low duty cycles.

To understand why the optimization knobs work, you need the two components of power consumption in a digital circuit. *Dynamic power* is the energy spent switching transistors — charging and discharging the capacitive loads as logic gates toggle between 0 and 1 — and it scales as $P_{\text{dyn}} = \alpha C V^2 f$, where $\alpha$ is the activity factor, $C$ is switched capacitance, $V$ is supply voltage, $f$ is clock frequency. Dynamic power dominates when the processor is active. Doubling the clock roughly doubles dynamic power at constant voltage; reducing voltage helps quadratically because of the $V^2$ term. *Static power* (also called leakage) is the current that flows through transistors even when they are not switching — through the gate oxide and junctions. Leakage depends on supply voltage, temperature (it rises exponentially with temperature), and process node (smaller transistors leak more per area). At room temperature on modern microcontrollers, static power is 1–10% of dynamic power when active, but it dominates in sleep mode because the dynamic power has been clock-gated away. Sleep current is essentially leakage.

The optimization strategy follows from this split. At *high duty cycle* (>50% active), reduce dynamic power: lower the clock, lower the voltage with DVFS, offload to a more efficient accelerator. At *low duty cycle* (<5% active), the active dynamic power barely matters because sleep dominates the average — reduce sleep current instead by enabling deeper sleep modes, gating peripheral power rails, and disabling everything that does not need to be on between inferences. *Minimize active time*, not active power, when sleep dominates the average.

![Two stacked bars showing average power composition by duty cycle. The high-duty-cycle bar (80% active) is mostly dynamic power with a sliver of leakage, captioned reduce V and f. The low-duty-cycle bar (1% active) is mostly leakage with a thin dynamic slice, captioned deepen sleep and gate peripherals.](../images/chapter-07-power-and-energy-fig-02.png)
*Figure 7.2 — Power composition shifts with duty cycle. The crossover near 5–10% active sets which optimization knob to turn.*

A common error is running inference at a low clock to "save power." If inference takes 400 ms at 64 MHz at 20 mA, or 200 ms at 128 MHz at 35 mA, with 5 µA sleep current and a 10-second cycle:

At 64 MHz: $I_{\text{avg}} = (20 \cdot 0.4 + 0.005 \cdot 9.6) / 10 = 0.85\ \text{mA}.$

At 128 MHz: $I_{\text{avg}} = (35 \cdot 0.2 + 0.005 \cdot 9.8) / 10 = 0.75\ \text{mA}.$

The faster clock with shorter active time wins by 12% on average power. This is *race to sleep* — finish inference as fast as possible and return to deep sleep, because sleep is so much cheaper than slowed-down activity. The crossover depends on the ratio of active to sleep current and on the duty cycle. For systems that spend more than 90% of the time asleep, race to sleep almost always wins. For continuously active systems, reducing the clock saves power.

![Two overlaid current-vs-time traces on the same 10-second window. Trace A at 64 MHz draws 20 mA for 400 ms then drops to a 5 µA sleep floor; Trace B at 128 MHz draws 35 mA for only 200 ms then drops to the same floor. Shaded integrals label 8.0 mJ and 7.0 mJ; the shorter, taller burst wins by 12% on average current.](../images/chapter-07-power-and-energy-fig-03.png)
*Figure 7.3 — Race to sleep. Faster clock, shorter active window, lower average power — because sleep is so much cheaper than slowed-down activity.*

The duty cycle itself is shaped by *inference scheduling* — how often you run inference and what wakes the system up. A wildlife camera running inference every 60 seconds with 150 ms of inference time has a duty cycle of 0.15 / 60 = 0.25%; at 50 mA active and 10 µA sleep, average is $(50 \cdot 0.0025) + (0.01 \cdot 0.9975) = 0.135$ mA, and a 2,000 mAh battery lasts about 14,800 hours, 617 days. Now suppose the application demands inference every 5 seconds to catch fast-moving animals. Duty cycle goes to 3%, average to 1.51 mA, battery life drops to 55 days. *Increasing inference rate by 12× shrinks battery life by 11×.*

Three scheduling patterns recur. *Periodic* inference runs at fixed intervals — simple, predictable, the right default for continuous-stream applications like environmental monitoring or health tracking. *Event-driven* inference runs only when a low-power sensor detects something worth running for: a PIR motion detector wakes the system, then the camera runs inference; a voice activity detector wakes the system, then the keyword spotter runs. For applications where the events of interest are rare relative to the polling interval, event-driven scheduling reduces duty cycle by 10–100× and reduces energy by the same factor — *if* the trigger mechanism's own power is genuinely lower than continuous inference. A PIR consuming 50 µA continuously, replacing periodic inference at 50 mA × 0.015 s every 10 s, easily wins. *Adaptive* inference varies the interval with context: a vibration-monitoring system runs frequent inference when vibration is high, infrequent inference when it is normal. The savings come from the fact that interesting moments are rare in most applications, and you can afford to spend energy on them only when they happen.

![Three parallel timelines over a 60-second window. The periodic row shows evenly spaced inference spikes every 10 seconds. The event-driven row shows a long sleep floor punctuated by a single PIR-triggered burst marked with a wake arrow. The adaptive row shows dense spikes inside a shaded high-activity window and sparse spikes outside it. Each row carries an average-current label.](../images/chapter-07-power-and-energy-fig-04.png)
*Figure 7.4 — Three scheduling patterns. Periodic is the safe default; event-driven wins when events are sparse; adaptive wins when they cluster.*

Energy harvesting changes the constraint. Instead of a fixed energy budget that depletes, a harvester gives you a power budget that has to balance in steady state. *Average power consumed ≤ average power harvested*, or the system fails. A 1 cm² solar cell in full sun generates roughly 10 mW (100 mW/cm² irradiance × 10% efficiency). If your system consumes 5 mW on average, it runs indefinitely. If it consumes 15 mW, it runs out of stored energy and dies. Harvesting is intermittent: solar drops to zero at night, vibration harvesters depend on machine operation, RF harvesting depends on transmitter proximity. The system has to store enough during high-harvest periods to survive the low ones. Two constraints emerge. Peak power: instantaneous draw during inference must not exceed the harvester's peak output, or you need a storage capacitor large enough to discharge through the inference burst. Average energy balance: total energy consumed over a full harvest cycle (often 24 hours for solar) must not exceed total energy harvested. A vibration-harvesting industrial sensor that generates 5 mW during 16 hours of motor operation has 80 mWh of daily energy budget. If inference every 60 seconds at 80 mA × 120 ms × 3.3 V = 0.032 J per inference, multiplied by 1,440 inferences a day, plus sleep at 0.066 mW × 24 h, the total is about 14 mWh — comfortable, with a 5.7× margin. If the application demands inference every 10 seconds, that is 8,640 inferences/day, 76 mWh of inference energy alone, and the total is now 77.6 mWh against 80 mWh harvested. The margin is 3%, which is gone the moment harvesting efficiency drops by 5% from temperature, vibration amplitude, or aging. The energy-harvesting constraint is unforgiving in a way the battery constraint is not — you cannot just specify a bigger battery, because the input power is fixed by the cell area and the environment.

Profiling actual power consumption is non-negotiable. Spec sheets give you ranges; real systems can land anywhere in those ranges depending on configuration. The standard method is a current-sense resistor between the supply and the device — typically 0.1 to 1 Ω, dropping a small voltage that is measured by an oscilloscope or a dedicated power profiler (Nordic's Power Profiler Kit II, the Keysight N6705C, the Joulescope) at high sampling rates, so you can see the individual inference burst and the sensor wake-up and the LoRa transmission as separate features in the current trace.

![An oscilloscope-style current trace over a two-second window showing one full duty cycle. Features in order: a 10 µA sleep floor, a narrow 15 mA sensor-acquisition spike, a taller 80 mA inference burst for 150 ms, a brief return to sleep, then a wide 100 mA LoRa transmit envelope, then sleep again. Each region is annotated with its energy in millijoules; the LoRa transmit dominates.](../images/chapter-07-power-and-energy-fig-05.png)
*Figure 7.5 — Annotated power profile of one duty cycle. The radio is the biggest single feature — finding this on a real device usually finds the binding constraint.* The pattern looks like: baseline sleep current (5–50 µA), a sensor-acquisition spike (10–50 ms at 5–20 mA), an inference spike (50–500 ms at 30–200 mA), and back to baseline. Energy per inference is the integral of $V \times I$ over the active interval; for a 3.3 V device with constant 80 mA and 150 ms active, energy is $3.3 \cdot 0.08 \cdot 0.15 = 0.0396\ \text{J} = 39.6\ \text{mJ}$. If inference happens every 30 seconds, average power is 1.32 mW, and a 2,000 mAh / 6,600 mWh / 23,760 J battery lasts $23{,}760 / 0.00132 \approx 18\ \text{million seconds}$, or 208 days. Add sleep current at 10 µA and the sleep contribution is 0.985 mJ per cycle on top of the 39.6 mJ of inference — a 2.4% adjustment, which is small here because duty cycle is low, but which dominates as duty cycle rises.

Profiling reveals surprises. Peripherals left enabled, GPIO pins floating and pulling leakage current, firmware bugs that prevent deep-sleep entry, communication modules whose "sleep" mode is not what the datasheet implied — any of these can double or triple the average current. The wildlife camera that drained batteries in three weeks almost certainly had one of these — likely a peripheral left active or an unintended wake-up keeping the part out of true deep sleep.

To make the workflow concrete, design a remote agricultural sensor on two AA alkaline cells (3 V, 2,850 mAh, 8,550 mWh, 30,780 J) for six-month deployment. The hardware: STM32L4 (1 µA deep sleep, 12 mA active at 80 MHz), a soil-moisture sensor (500 µA when powered), and a LoRaWAN radio (40 mA transmit, 1 µA sleep). The model is a small int8 anomaly detector — 100,000 parameters, 15 M MACs per inference, measured 220 ms latency at 12 mA. Target average power for six months is $30{,}780 / (4{,}380 \cdot 3{,}600) = 1.95\ \text{mW}$.

Periodic inference every ten minutes: per cycle (600 s), sensor 7.5 mJ, inference 7.92 mJ, LoRa amortized from once-per-hour 10 mJ, sleep 1.78 mJ, total 27.2 mJ. Average power 0.045 mW. Battery life would be 21 years if nothing else mattered — the constraint is not even close to binding.

Periodic inference every minute: per cycle (60 s), sensor 7.5 mJ, inference 7.92 mJ, LoRa 1 mJ, sleep 0.155 mJ, total 16.6 mJ. Average power 0.277 mW. Battery life 3.5 years. Still huge margin.

Continuous inference every second: per cycle (1 s), sensor 7.5 mJ, inference 7.92 mJ, LoRa 0.017 mJ, sleep 0.0008 mJ, total 15.4 mJ. Average power 15.4 mW. Battery life 23 days. *Now* the constraint is violated, and dramatically so. Continuous inference is the wrong scheduling pattern for this application.

The interesting result is that the binding constraint here is not inference at all — it is *communication*. Each LoRa transmission costs 60 mJ; with hourly transmission the average is 16.7 mW, with six-hour transmission the average drops to 2.78 mW. Reducing LoRa from once per hour to once per six hours, with one-minute inference, gets the system to about 0.26 mW average and a battery life close to 4 years. The model could run more often than once a minute and the system would still be fine. The application's binding number is not the inference frequency; it is the radio.

![Battery-life curve for the agricultural sensor. X-axis: inference period from 1 to 600 seconds, log scale. Y-axis: battery life in days, log scale. Four overlaid curves for LoRa intervals — 1/hour, 1/6 hours, 1/day, and no radio. A dashed line marks the 180-day six-month target. The three scheduling examples from the chapter are marked as points on the 1/hour curve. Above the target line lives only when LoRa drops to 1/day or vanishes.](../images/chapter-07-power-and-energy-fig-06.png)
*Figure 7.6 — Battery life vs inference period. The radio sets the ceiling; the inference axis barely matters once the radio is set.*

When the power budget cannot be met, the moves are roughly the moves we already saw in Chapter 1's design space, plus a few specific to power. A larger battery or a harvester gets you more energy at the cost of size, weight, and BOM. Faster inference at higher clock often *reduces* energy per inference because of race-to-sleep. Event-driven triggering reduces inference frequency by 10–100× when the events of interest are sparse. Cloud offload moves the cost from inference energy to communication energy, which is the right trade if the application's network is cheap and not the right one if it is not. Power is the constraint with the most knobs, because duty cycle is a free variable in a way that processor speed and memory size are not — you can almost always reduce average power by running less often, and the question is whether running less often still meets the application requirement. If yes, power is solvable. If no, the choice of hardware, model, or system architecture was wrong, and the next chapter's tools — hardware accelerators that execute AI operations faster and more efficiently than general-purpose cores — are one of the directions that opens up.

---

## LLM Exercise — Chapter 7: Power and Energy

**Project:** TinyML Feasibility Toolkit
**What you're building this chapter:** The power verdict module — energy-balance equation, average power, battery-life prediction, and duty-cycle recommendations.
**Tool:** Claude Code

---

**The Prompt:**

```
Add src/tinyml_feasibility/power.py to the tinyml-feasibility toolkit.

Frozen PowerVerdict dataclass:
- active_energy_mj: float (energy per inference)
- sleep_power_mw: float
- duty_cycle_s: float (inference period from app config)
- average_power_mw: float
- battery_life_days: float | None (None if no battery_mah in app config)
- power_budget_mw: float
- headroom_pct: float
- verdict: Literal["FITS", "TIGHT", "FAILS"]
- mitigations: list[str]
- to_markdown() emits a Power section matching Chapter 14's shape

Public function:
`assess_power(model: ModelSummary, target: Target, app: Application, latency_estimate: LatencyEstimate) -> PowerVerdict`

Implementation:
- active_current_ma = target.active_current_ma_per_mhz * target.clock_mhz
- active_power_mw = active_current_ma * supply_voltage (default 3.3V; configurable)
- active_energy_mj = active_power_mw * latency_estimate.total_ms / 1000
- sleep_power_mw = target.sleep_current_ua * supply_voltage / 1000
- average_power_mw = (active_energy_mj / duty_cycle_s) + sleep_power_mw
- battery_life_days = (battery_mah * supply_voltage * 3.6 / 1000) / (average_power_mw / 1000) / 86400 (only if app.battery_mah set)
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

---

## Prompts

Use these prompts with Claude to generate interactive D3 v7 versions of the figures in this chapter. Each produces a standalone HTML file you can open in a browser and modify.

**Prerequisites:** Load `brutalist/CLAUDE.md` and `brutalist/DESIGN.md` into your Claude project context. They define the stack, naming conventions, color system, and typography these figures use.

---

### Figure 7.1 — Same average power, two current profiles

Build a two-panel D3 v7 figure comparing two current-vs-time traces that share an average power of 10 mW. Left panel: a steady 3 mA continuous draw across the full 10-second window. Right panel: a duty-cycled trace with 60 mA bursts of 150 ms duration recurring every 3 seconds over a 0.15 mA sleep floor. Chart type: stepped line + area fill, log-scaled y-axis from 0.1 to 200 mA, linear x-axis in seconds. Channels: x = time (linear), y = current (log). Use `var(--color-ink)` for trace, `var(--color-secondary)` 25% opacity for area fill. Title each panel with its scheme; annotate that both shaded areas integrate to the same energy. Tooltip on hover reports time and instantaneous current. Standalone HTML, D3 7.9.0 from the pinned CDN, accessible (role, title, desc), ResizeObserver redraw, `prefers-reduced-motion` suppression.

> Reference implementation: `d3/chapter-07-power-and-energy-fig-01.html`

---

### Figure 7.2 — Power composition by duty cycle

Build a single D3 v7 stacked column chart with two columns, each normalised to total share (0–100%). Column A — High duty cycle (80% active): dynamic 96%, leakage 4%; subtitle "avg ≈ 12 mW"; mitigation label above bar reads "reduce V and f · DVFS · accelerator offload". Column B — Low duty cycle (1% active): dynamic 17%, leakage 83%; subtitle "avg ≈ 0.6 mW"; mitigation label reads "deepen sleep · gate peripherals". Chart type: vertical stacked bars. Channels: x = duty regime (band), y = share (linear 0–1). Dynamic segment uses `var(--color-ink)`; leakage segment uses `var(--color-secondary)`. Mitigation labels use `var(--color-ochre)`. y-axis ticks formatted as percentages. Tooltips show segment percent per bar. Standalone HTML, D3 7.9.0, accessible, ResizeObserver, reduced-motion safe.

> Reference implementation: `d3/chapter-07-power-and-energy-fig-02.html`

---

### Figure 7.3 — Race to sleep

Build a single D3 v7 dual-trace current-vs-time chart over a 1.2-second window inside a 10-second duty cycle. Trace A (64 MHz): step from 20 mA at t=0 to a 0.005 mA sleep floor at t=0.4 s. Trace B (128 MHz): step from 35 mA at t=0 to the same floor at t=0.2 s. Chart type: overlaid stepped lines with light area fills underneath. Channels: x = time (linear, seconds), y = current (log, 0.001–50 mA). Trace A uses `var(--color-ink)`; Trace B uses `var(--color-red)`. Include legend with computed energy per active phase (8.0 mJ vs 7.0 mJ) and an annotation "shorter and taller wins — 12% lower average". Standalone HTML, D3 7.9.0, accessible markup, ResizeObserver, reduced-motion safe.

> Reference implementation: `d3/chapter-07-power-and-energy-fig-03.html`

---

### Figure 7.4 — Three scheduling patterns

Build a D3 v7 three-row swimlane chart over a shared 60-second x-axis. Lane 1 — Periodic: inference spikes at t = 5, 15, 25, 35, 45, 55. Lane 2 — Event-driven: a single PIR-wake spike at t = 28 colored in `var(--color-red)`. Lane 3 — Adaptive: dense spikes at t = 22, 25, 28, 31, 34, 37 inside a shaded "high-activity window" rectangle from t = 20 to 40, plus sparse spikes at t = 6 and 50. Chart type: categorical swimlanes (scaleBand on y) with rectangular event marks (4 px wide). Channels: x = time (linear seconds), y = lane (band). Left margin holds per-lane label, sub-label, and average-current chip. Activity band uses `var(--color-ochre)` at 18% opacity. Tooltips show event time and lane. Standalone HTML, D3 7.9.0, accessible, ResizeObserver, reduced-motion safe.

> Reference implementation: `d3/chapter-07-power-and-energy-fig-04.html`

---

### Figure 7.5 — Annotated power profile

Build a single D3 v7 stepped current-vs-time chart over a 2-second window. Trace points (mA): sleep floor 0.01 from t=0 to 0.35, sensor 15 from 0.35 to 0.38, sleep, inference 80 from 0.55 to 0.70, sleep, LoRa 100 from 0.95 to 1.65, sleep until 2.0. Chart type: stepped line with shaded feature regions. Channels: x = time (linear), y = current (log, 0.001–200 mA). Render four shaded rectangles — sensor (`var(--color-secondary)`), inference (`var(--color-ink)`), LoRa (`var(--color-red)`) — at 18–22% opacity. Label each region with feature name above and energy in mJ below (1.5 / 39.6 / 231). Add a top-right callout "radio = 85% of energy bill · total ≈ 272 mJ" in `var(--color-red)`. Tooltip on each region reports peak current and energy. Standalone HTML, D3 7.9.0, accessible, ResizeObserver, reduced-motion safe.

> Reference implementation: `d3/chapter-07-power-and-energy-fig-05.html`

---

### Figure 7.6 — Battery life vs inference period

Build a single D3 v7 multi-line chart for the agricultural sensor. Compute battery life in days for inference periods from 1 to 600 s (log scale) at four LoRa intervals: 1/hour, 1/6 h, 1/day, no radio. Energy model (mJ): inference 7.92 per cycle + sensor 7.5 per cycle + sleep 3.3 µW + LoRa 60 mJ per transmit. Budget: 8,550 mWh on two AA cells. Chart type: log-log line chart. Channels: x = inference period (log seconds), y = battery life (log days). Use `var(--color-ink)` for the three LoRa curves (solid, dashed 6 3, dotted 2 3) and `var(--color-ochre)` for the no-radio curve. Add a dashed `var(--color-red)` horizontal target line at 180 days labeled "180-day target". Mark sample points at inference periods of 1, 60, 600 s on the 1/hour curve with hover tooltips. Standalone HTML, D3 7.9.0, accessible, ResizeObserver, reduced-motion safe.

> Reference implementation: `d3/chapter-07-power-and-energy-fig-06.html`

---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Rolf Landauer** proved that erasing a single bit of information costs a minimum amount of energy — kT ln 2, set by physics — and every joule your inference burns is paying some multiple of that bill.

**Run this:**

```
Who was Rolf Landauer, and how does his principle on the thermodynamic cost of erasing information connect to the energy budget of embedded inference? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"Rolf Landauer"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain Landauer's principle in plain language, with one physical analogy
- Ask it to compare Landauer's lower bound to the actual energy per inference on a modern microcontroller
- Add a constraint: "Answer as if you're writing one paragraph for a physics-of-computation textbook"

What changes? What gets better? What gets worse?
