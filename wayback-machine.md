# AI Wayback Machine — embedded-ai

*Companion file. One figure per chapter, a copy-paste-ready prompt, a Wikipedia search nudge, and three "make it better" suggestions tied to the chapter and the figure. Inserted at the bottom of each chapter file in `chapters/`.*

---

## Chapter 1 — Annie Easley

```markdown
---

## AI Wayback Machine

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
```

---

## Chapter 2 — Lynn Conway

```markdown
---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Lynn Conway** co-wrote the textbook that turned chip design from black art into a set of design rules — turning silicon constraints into variables you could reason about, decades before tinyML.

**Run this:**

```
Who was Lynn Conway, and how does her work on VLSI design methodology with Carver Mead connect to treating hardware constraints as design variables? Three paragraphs. End with the single most surprising thing about her career.
```

→ Search **"Lynn Conway"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain "design rules" in chip design as if you've never seen a circuit
- Ask it to compare Conway's VLSI revolution to today's struggle to make embedded ML deployment systematic
- Add a constraint: "Answer in the form of a single page from a 1980s engineering textbook"

What changes? What gets better? What gets worse?
```

---

## Chapter 3 — Lotfi Zadeh

```markdown
---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Lotfi Zadeh** invented fuzzy logic — a way to make machines reason about "warmer," "almost full," "a little wobbly" — and it ran in millions of embedded controllers (cameras, rice cookers, subway brakes) long before deep learning shipped on microcontrollers.

**Run this:**

```
Who was Lotfi Zadeh, and how does his work on fuzzy logic and approximate reasoning connect to embedded machine learning today? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"Lotfi A. Zadeh"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain fuzzy logic in plain language, with one washing-machine example
- Ask it to compare a fuzzy controller to a small neural network solving the same control problem
- Add a constraint: "Answer as if you're writing a footnote in a textbook on embedded ML"

What changes? What gets better? What gets worse?
```

---

## Chapter 4 — Thelma Estrin

```markdown
---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Thelma Estrin** built one of the first real-time biomedical computing systems — getting EEG signals into a computer fast enough to be useful — when "real-time" still meant tape and paper.

**Run this:**

```
Who was Thelma Estrin, and how does her work on real-time biomedical computing at UCLA connect to today's inference pipelines on embedded processors? Three paragraphs. End with the single most surprising thing about her career.
```

→ Search **"Thelma Estrin"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain what real-time biomedical signal processing meant in the 1960s, in plain language
- Ask it to compare Estrin's EEG digitization pipeline to a modern wearable's inference pipeline
- Add a constraint: "Answer in the form of an oral-history interview transcript"

What changes? What gets better? What gets worse?
```

---

## Chapter 5 — An Wang

```markdown
---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **An Wang** invented magnetic core memory — the technology that stored every bit in every computer for two decades, the spiritual ancestor of the SRAM you're allocating tensors into now.

**Run this:**

```
Who was An Wang, and how does his work on magnetic core memory connect to the SRAM and flash trade-offs in modern embedded AI systems? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"An Wang"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain how magnetic core memory worked, in plain language
- Ask it to compare core memory's energy and access cost to today's SRAM, in numbers
- Add a constraint: "Answer as if you're explaining it to an embedded engineer who has only ever used flash and SRAM"

What changes? What gets better? What gets worse?
```

---

## Chapter 6 — Frances Allen

```markdown
---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Frances Allen** invented the techniques that turn a high-level loop into the SIMD instructions you're now counting cycles on — vectorizing compilers, decades before CMSIS-NN.

**Run this:**

```
Who was Frances Allen, and how does her work on vectorizing compilers and program optimization connect to running int8 inference on a SIMD-equipped microcontroller? Three paragraphs. End with the single most surprising thing about her career.
```

→ Search **"Frances E. Allen"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain what a vectorizing compiler does, with one tiny C example
- Ask it to compare Allen's compiler optimizations to what CMSIS-NN does for a Cortex-M4
- Add a constraint: "Answer as if you're writing the dedication page of a compiler textbook"

What changes? What gets better? What gets worse?
```

---

## Chapter 7 — Rolf Landauer

```markdown
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
```

---

## Chapter 8 — Carver Mead

```markdown
---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Carver Mead** coined the term "neuromorphic engineering" and built analog circuits that imitated biological neurons in silicon — the deep history of every NPU on the market today.

**Run this:**

```
Who was Carver Mead, and how does his work on neuromorphic engineering and analog VLSI connect to today's NPUs and AI accelerators? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"Carver Mead"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain what "neuromorphic" means in plain language, with one analog circuit example
- Ask it to compare Mead's analog approach to a digital NPU like the Ethos-U55 or Syntiant NDP120
- Add a constraint: "Answer in the form of a footnote in a hardware-for-ML textbook"

What changes? What gets better? What gets worse?
```

---

## Chapter 9 — Radia Perlman

```markdown
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
```

---

## Chapter 10 — Chung Laung Liu

```markdown
---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Chung Laung "C.L." Liu** co-authored the 1973 paper on rate-monotonic scheduling — the math behind every hard-real-time system that has to guarantee a deadline, including the AI ones.

**Run this:**

```
Who was C.L. Liu, and how does his work with James Layland on rate-monotonic scheduling connect to today's hard real-time embedded AI systems? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"Chung Laung Liu"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain rate-monotonic scheduling in plain language, with one tiny example
- Ask it to compare the Liu-Layland bound (~69%) to the safety margin you'd want when an AI inference task shares a CPU with control loops
- Add a constraint: "Answer as if you're writing a footnote in a real-time systems textbook"

What changes? What gets better? What gets worse?
```

---

## Chapter 11 — Vilfredo Pareto

```markdown
---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Vilfredo Pareto** was an Italian economist studying income distribution in 1906 when he formalized the idea that some allocations are dominated and some are not — the same Pareto frontier you used to choose between MobileNet variants.

**Run this:**

```
Who was Vilfredo Pareto, and how does his work on Pareto efficiency in economics connect to selecting embedded ML models on an accuracy-latency frontier? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"Vilfredo Pareto"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain Pareto efficiency in plain language, with one non-economics example
- Ask it to compare Pareto's original economics frontier to a modern accuracy-vs-latency frontier for embedded models
- Add a constraint: "Answer as if you're writing a sidebar in an econ-meets-engineering textbook"

What changes? What gets better? What gets worse?
```

---

## Chapter 12 — Jacob Ziv

```markdown
---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Jacob Ziv** co-invented the LZ77 and LZ78 algorithms — the lossless-compression theory that underlies every ZIP file. Quantizing a neural network is the lossy cousin: same idea, different trade-off.

**Run this:**

```
Who was Jacob Ziv, and how does his work on lossless compression with Abraham Lempel connect to lossy techniques like int8 quantization and pruning in embedded ML? Three paragraphs. End with the single most surprising thing about his career.
```

→ Search **"Jacob Ziv"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain how LZ77 compression works in plain language, with one tiny example
- Ask it to compare lossless LZ compression to lossy int8 quantization on the same trade-off axes
- Add a constraint: "Answer as if you're writing a chapter epigraph for a model-compression textbook"

What changes? What gets better? What gets worse?
```

---

## Chapter 13 — Sophie Wilson

```markdown
---

## AI Wayback Machine

The ideas in this chapter didn't appear from nowhere. **Sophie Wilson** designed the original ARM instruction set in 1983 — the architecture every Cortex-M chip in this book inherits, the silicon your `.tflite` ultimately gets compiled down to.

**Run this:**

```
Who was Sophie Wilson, and how does her design of the original ARM instruction set connect to running quantized neural networks on Cortex-M microcontrollers today? Three paragraphs. End with the single most surprising thing about her career.
```

→ Search **"Sophie Wilson"** on Wikipedia. See what the model got right, got wrong, or left out.

**Now make the prompt better.** Try one of these:

- Ask it to explain what an instruction set is, in plain language, as if you've never seen assembly
- Ask it to compare the design choices in the original ARM ISA to the choices that make CMSIS-NN fast on Cortex-M
- Add a constraint: "Answer as if you're writing the foreword to an ARM assembly programming book"

What changes? What gets better? What gets worse?
```

---

## Chapter 14 — W. Ross Ashby

```markdown
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
```

---

## Diversity Summary

**Figures included:** Annie Easley, Lynn Conway, Lotfi Zadeh, Thelma Estrin, An Wang, Frances Allen, Rolf Landauer, Carver Mead, Radia Perlman, Chung Laung Liu, Vilfredo Pareto, Jacob Ziv, Sophie Wilson, W. Ross Ashby.

**Gender breakdown:** 6 women (43%, including 2 trans women — Conway, Wilson) / 8 men (57%).

**Geographic / national breakdown:**
- US (born or naturalized): Easley (Black American), Conway, Estrin (Polish-Jewish heritage), Wang (Chinese-American), Allen, Mead, Perlman, Liu (Taiwan/American)
- UK: Wilson, Ashby
- Iran/Azerbaijan → US: Zadeh
- Germany → US (Jewish refugee from Nazi Germany): Landauer
- Italy: Pareto
- Israel: Ziv

**Era breakdown:**
- Pre-1950 (born): Pareto (1848), Ashby (1903), Allen (1932) — actually post-1950 active
- Pre-1950 active: Pareto, Wang (started early 1950s), Ashby (1940s)
- Mid-20th century active: Easley, Estrin, Wang, Allen, Landauer, Ashby, Mead, Liu
- Late 20th century active: Conway, Zadeh, Mead, Perlman, Liu, Ziv, Wilson

**Disciplines represented:** flight software / NASA computing, VLSI design methodology, fuzzy logic / approximate reasoning, biomedical computing / signal processing, magnetic core memory hardware, vectorizing compilers, physics of computation / thermodynamics, neuromorphic engineering, network protocol design, real-time scheduling theory, economics / multi-criteria optimization, information theory / lossless compression, computer architecture / instruction set design, cybernetics / systems theory.

**Flags:**
- Western skew remains: no figures from continental Africa, South Asia, Latin America, Southeast Asia, or Indigenous traditions. Two from Asia (Wang, Liu — both East Asian, both eventually US-based). One from the Middle East (Zadeh). The set is more diverse than the standard Turing/Shannon/von Neumann roster but is still concentrated in the US-UK-European axis with East Asian additions.
- Gender ratio (6F / 8M) is reasonable but could go higher with effort.
- Trans representation: 2 of 14 (Conway, Wilson) — both happen to be central to computing, not tokens.
- Era spread is narrow on the very early end (Pareto is the only pre-20th-century figure); the math-heavy chapters (10, 11, 12) lean toward the standard mid-20th-century pioneer profile.
