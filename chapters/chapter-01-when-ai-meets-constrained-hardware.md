# Chapter 1 — When AI Meets Constrained Hardware

On November 12, 2019, a smart doorbell shipped by a well-known home-security company began draining its battery in forty-eight hours instead of the advertised six months. The hardware hadn't changed. The battery hadn't changed. Three weeks earlier the device had received a firmware update that added person detection using an on-device neural network, and after the update the product fell over in production. Twelve thousand units came back in the first month. The feature was rolled back by December.

Nothing was catastrophic. No one was hurt, no homes were burgled because a doorbell died. The interesting thing about the failure is that it was not really an engineering error in the usual sense. The team had tested the AI model. They had verified its accuracy. They had confirmed it could run on the device's processor. What they had not done was measure how much power the model consumed during continuous operation, compare that consumption against the device's sleep/wake duty cycle, and project battery life under realistic conditions. They had treated the model as software that happens to run on hardware, rather than as a design decision with resource consequences that had to be quantified before deployment.

That distinction is the entire subject of this book. Artificial intelligence and embedded systems live in tension with one another, and that tension produces design constraints you cannot ignore. The doorbell is one of many ways that ignoring them looks. Once you have the apparatus this book builds, you'll be able to read the doorbell story and see exactly which calculation was missing — not in retrospect, but ahead of time, before the firmware ships.

To get there we have to start with what *embedded* actually means.

The word is loose in casual usage. People reach for it as a synonym for *small*, or *low-cost*, or *IoT*. Those correlations exist, but they don't define the thing. A Raspberry Pi 4 is not constrained the way an Arduino Nano 33 is constrained, even though both get called embedded. A Tesla's autopilot computer has more compute than most laptops; it is also embedded. What makes a system embedded is not size. It is that the system has been purpose-built for a specific application, with its resources allocated to do that one thing, and there is no overhead left over for generality.

The operational consequence of that definition is the first principle you need: *resources are fixed, and exceeding them is not recoverable*. A laptop can swap memory to disk when RAM runs out. A cloud server can autoscale compute when demand spikes. A desktop GPU can pull three hundred watts from a wall socket without consequence. Embedded systems can do none of these things. They have the memory they shipped with. They have the processor they were designed around. They have a power budget set by a battery, an energy harvester, or a constrained supply rail. When you exceed those limits, the system does not slow down gracefully. It fails.

Now bring AI into that environment. The thing that makes integration hard is not a lack of skill on either side. It is a mismatch in what the two artifacts assume.

A neural network is general-purpose. A model trained to detect faces does not know it is going to run on a battery-powered camera. It does not care whether the processor has a floating-point unit, whether SRAM is shared with the communication stack, or whether the duty cycle of the sensing pipeline can support its compute load. The model's resource requirements were fixed when it was trained — by its architecture, its layer sizes, its weight precision, its arithmetic — and those requirements do not negotiate. The embedded system, on the other hand, has its own fixed budget, set by cost, power, thermal envelope, and what the application actually does. Integration is the design problem you get when you try to fit a fixed-resource-demand artifact into a fixed-resource-supply environment.

Here is what that looks like at the bench.

Imagine a wearable health monitor — a wristband that tracks heart rate, activity, and sleep. It runs on a coin-cell battery that has to last fourteen days between charges. It has 256 KB of SRAM, 1 MB of flash, a 64 MHz microcontroller with no hardware floating-point unit. None of those numbers are negotiable. Industrial design wants the device small and light, so the battery has to be a coin cell. Cost targets keep the microcontroller cheap, which means no FPU. The fourteen-day battery life is the competitive threshold. The device must do its job inside those numbers or it doesn't ship.

Now you want to add on-device arrhythmia detection with a small recurrent neural network. The model has been trained, achieves 94% accuracy on validation, requires 180 KB for weights, 60 KB for activation buffers during inference, and runs about 22 million multiply-accumulates per pass. The model *runs*. The question is whether it fits.

Memory: 180 KB plus 60 KB is 240 KB. You have 256 KB. That leaves 16 KB for the rest of the firmware — sensor drivers, Bluetooth stack, UI, power management. Tight, but with care, possible.

Compute: at 64 MHz with no FPU, the processor can sustain about 64 million integer operations per second. Floating-point operations have to be emulated in software, which costs a factor of ten or more in throughput. So 22 million floating-point multiply-accumulates becomes roughly 220 million equivalent integer operations, which is about 3.4 seconds of processor time per inference pass. The application requires inference every 30 seconds to catch arrhythmia events, so the processor is awake 3.4 seconds out of every 30 — an 11% duty cycle.

That duty cycle determines power. Suppose the processor draws 15 mA active and 5 µA asleep. Average current is roughly 1.7 mA. A 220 mAh coin cell will sustain that for about 130 hours — five days, not fourteen. The integration *fails the battery-life constraint*.

Notice what just happened. The model did not crash. It produced correct results. The hardware did not malfunction. The system performed exactly as designed, and the design was wrong, because the design was made without doing the calculation we just did. This is what the doorbell story actually was.

So why not just put the model in the cloud? That is the obvious move, and for a long time it was the dominant move. Alexa sends your voice to Amazon's servers. Google Photos runs recognition in the cloud. Early autonomous vehicles uploaded sensor data for post-processing. The cloud has unbounded memory and unbounded compute, and you do not have to fight any of the math we just did. So why does this book exist at all?

Because for an entire class of applications, the cloud architecture has stopped working — and the reasons it has stopped working are not engineering shortcomings that can be fixed by faster servers or better networks. They are properties of the application itself. Four of them, specifically.

*Latency.* Round-tripping a sensor reading to a server and back has a floor set by the speed of light, the network stack, and the queueing inside the server. On a fast local network the round trip is at least 50 ms; over cellular it can be hundreds. If the application is a robotic arm classifying a part on a moving conveyor with a 100 ms inspection window, the cloud round trip closes the window before the answer arrives. The application requires on-device inference not because the cloud is slow but because the cloud is too slow for *this clock*.

*Privacy.* Some data cannot leave the device. Cardiac wearables and seizure detectors handle protected health information governed by HIPAA in the United States and GDPR in Europe. Even with user consent, the regulatory and liability load of streaming raw physiological data to a server often makes cloud inference non-viable. The same logic applies to home-security cameras, workplace monitors, and many other domains. Run the model where the sensor is, and let only the result leave.

*Connectivity.* For some deployments the network is intermittent, expensive, or absent. Agricultural sensors in remote fields may see cellular service only when a vehicle drives by. Underwater inspection drones have no real-time uplink. Disaster-response robots enter environments where the infrastructure has failed. The model must run locally because the alternative is not *slower inference*; it is *no inference*.

*Cost.* Bandwidth costs money. A parking sensor that sends a few bytes an hour can run for years on a coin cell; the same sensor streaming video to a cloud detector cannot. For high-volume, low-margin deployments, the recurring cost of network transmission can exceed the cost of the hardware. On-device inference shifts cost from operational expense to capital expense, which for many products is the only way the deployment closes economically.

These four — latency, privacy, connectivity, cost — define the boundary where cloud AI stops working and edge AI becomes necessary. They do not determine whether edge AI is *feasible*, only whether it is *required*. Whether you can actually deliver it depends on whether your hardware can carry the model. That is where the four constraint categories come in, and these are the spine of the rest of the book.

*Memory* determines what you can store. A trained network is a large data structure: millions of weight parameters, layer configurations, activation buffers. All of it has to fit. Embedded processors typically have two memory regions. Flash is non-volatile, abundant, slow, and read-only at runtime. SRAM is fast, writable, and scarce — often kilobytes, not megabytes. Weights can live in flash, but the activations during inference have to live in SRAM. If activation memory exceeds available SRAM, the model cannot run, no matter how big your flash is.

*Compute* determines how fast you can run. Inference is a fixed sequence of operations — matmuls, convolutions, activations — and the time to complete one pass is set by the operation count, the processor's throughput, and whether you have specialized hardware (FPU, NN accelerator, SIMD lanes) to exploit. Compute shows up as latency. For some applications the latency is soft — a few hundred milliseconds is fine. For others it is hard — miss the deadline and the result is useless.

*Power* determines how long you can run. Every operation costs energy. Every memory access costs energy. The energy comes from a finite source. If average power exceeds the available budget, the device's battery shrinks below tolerance, the thermal envelope is violated, or the supply rail collapses. For battery-powered devices, power is usually the binding constraint, which is exactly the case the doorbell ran into.

*Real-time performance* determines whether you can meet deadlines. Real-time is not a synonym for fast. A real-time system is one where correctness depends not just on producing the right result but on producing it *by* a specific time. Soft real-time can tolerate occasional misses; hard real-time cannot. Inference complicates this because execution time can vary with input data, cache state, memory contention, and scheduler decisions. For hard real-time deployment, worst-case execution time has to be bounded and provable, which is hard for models with attention or conditional branches.

These four are not independent. They couple in ways that matter. Quantizing weights from 32-bit float to 8-bit integer cuts memory and speeds up inference because there are fewer bytes to move, but it can degrade model accuracy. Offloading inference to a hardware accelerator cuts latency and power but adds cost and integration complexity. Running inference at a lower duty cycle reduces average power but increases response latency. Every design decision in embedded AI is a trade among these four, and the practitioner who cannot quantify the trade cannot make the decision.

To make the coupling concrete, take a keyword-spotter — a wake-word model listening for *Hey, device*. The model is a small CNN trained on audio spectrograms. 42,000 parameters. 180 KB of memory between weights and activations. 1.8 million ops per pass. Inference must finish within 100 ms to feel responsive. The device runs on a 1000 mAh lithium-ion battery and has to last a week of continuous listening.

Two candidate processors. *Target A*: ARM Cortex-M4 at 80 MHz, 256 KB SRAM, hardware FPU, 1 MB flash, 20 mA active, 10 µA asleep, $3 per unit. *Target B*: ARM Cortex-M0+ at 48 MHz, 32 KB SRAM, no FPU, 256 KB flash, 8 mA active, 2 µA asleep, $0.80 per unit.

Target A: the 180 KB fits in 256 KB SRAM. The FPU lets the processor sustain about 80 MFLOPS, so 1.8 million ops take roughly 22 ms — well inside the 100 ms latency budget. If inference runs once every 100 ms, the duty cycle is 22% and the average current is about 4.4 mA. A 1000 mAh cell at that draw lasts roughly 227 hours — about nine days. Tight on the one-week target, but workable.

Target B: 180 KB does not fit in 32 KB SRAM. The model fails the memory check before you even reach compute. Even if you somehow compressed it, the absence of an FPU means floating-point ops are emulated, throughput drops by an order of magnitude, the inference takes 375 ms or longer, and latency fails too.

Target B is one-quarter the cost of Target A. For a consumer device with tight margins and high volume, that gap is decisive. So now you face a real engineering choice: accept the higher unit cost, or modify the model to fit. Modifying means quantizing weights to int8, pruning, switching to a depthwise-separable architecture — each of which changes accuracy. If accuracy drops below the application's threshold, the savings buy you a product that does not work. That is the design space. Two surfaces — what the model demands and what the hardware can supply — and the question is whether they overlap.

When they do not overlap, you have three moves. Change the model. Change the hardware. Change the requirements. There is no fourth move. The doorbell team at the start of this chapter had a fourth move on their whiteboard — *integrate and ship* — and the universe declined to honor it.

The rest of this book is a toolkit for not making that mistake. Each chapter adds one dimension of analysis. By the end you should be able to take a sensing task, an application requirement, and a hardware target, and decide — with numbers, before any code is written — whether deployment is feasible, what model and deployment strategy will make it feasible if it is, and which trade-offs you have just chosen and which alternatives you have just declined.

That skill does not make you a machine-learning researcher. It does not make you an embedded-systems architect. It makes you a systems integrator who can reason across both domains. That is what the field needs, and that is what most of the field currently lacks.

The next chapter starts with the constraints themselves, in the units the datasheets are actually written in.

---

## 🛠️ LLM Exercise — Chapter 1: When AI Meets Constrained Hardware

**Project:** TinyML Feasibility Toolkit (Python CLI)
**What you're building this chapter:** The package scaffold, the `Application` dataclass, and a CLI that loads a YAML application spec and reports the four constraint targets.
**Tool:** Claude Code

---

**The Prompt:**

```
Set up a new Python package called `tinyml-feasibility`. By chapter 14 it will take a trained ML model and a target microcontroller spec and produce a deployment-feasibility report grounded in the four-constraint framework (memory, compute, power, real-time).

Scaffold:
- pyproject.toml (PEP 621, Python 3.10+, hatchling backend)
- src/tinyml_feasibility/__init__.py exposing __version__
- src/tinyml_feasibility/cli.py — Click-based CLI
- src/tinyml_feasibility/application.py — frozen Application dataclass with fields: name (str), description (str), latency_budget_ms (int), real_time_class (Literal["soft","firm","hard"]), memory_budget (nested dataclass with flash_kb and sram_kb, both int), power_budget_mw (float), accuracy_floor_pct (float), bom_ceiling_usd (float). Type hints on every field.
- src/tinyml_feasibility/schemas/application.example.yaml — a real worked example for a wildlife acoustic sensor or comparable application
- tests/test_cli.py with three passing tests
- README.md (one paragraph: what the toolkit will do by chapter 14)
- LICENSE (MIT)

CLI commands at this stage:
- `tinyml-feasibility --version` prints the version
- `tinyml-feasibility check-app <path-to-app.yaml>` loads the YAML and prints the four constraint targets in plain English

Tests:
- test_version_prints — exit code 0, stdout matches expected
- test_check_app_loads_example — runs against schemas/application.example.yaml, asserts all four budget values appear in output
- test_check_app_rejects_invalid — feeds malformed YAML, asserts exit code != 0 with a useful error message

Use the src/ layout. Run `pip install -e .` and `pytest` after writing — both must pass before you stop.
```

---

**What this produces:** A pip-installable Python package with `tinyml-feasibility check-app <yaml>` working end-to-end, three passing tests, and a documented YAML schema.

**How to adapt this prompt:**
- *For your own project:* Edit `application.example.yaml` to describe your application. Everything downstream reads from this file.
- *For ChatGPT / Gemini:* Works as-is — both handle multi-file scaffolding well.
- *For Claude Code:* Best fit. Use `--allowed-tools edit,bash`; Claude Code installs and runs `pytest` itself.
- *For a Claude Project:* Put the four-constraint framework and the YAML schema in the system prompt so subsequent chapters don't have to re-explain.

**Connection to previous chapters:** None — chapter 1.

**Preview of next chapter:** Chapter 2 adds the `Target` dataclass (microcontroller specs from datasheets) and a `Constraints` translator that converts `Application` + `Target` into the four-constraint object the rest of the toolkit reasons over.

---

## 🕰️ AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Annie Easley** wrote rocket-booster code in machine language for NASA's Centaur upper stage — software so constrained that every byte was hand-counted, decades before "embedded AI" was a phrase.

**Run this:**

```
Who was Annie Easley, and how does her work on the Centaur upper stage at NASA Lewis Research Center connect to writing code under hard memory and timing constraints? Three paragraphs. End with the single most surprising thing about her career.
```

→ Search **"Annie Easley"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain hand-coding in machine language in plain language, as if you've never written firmware
- Ask it to compare Easley's flight-software discipline to how a modern team would ship a constrained embedded ML pipeline today
- Add a constraint: "Answer as if you're writing the placard for a NASA history-of-computing exhibit"

What changes? What gets better? What gets worse?
