# Embedded AI — Batch Build Log

35 claude-explainer (claude-liam) videos built in one batch from two card lists.
Build started: 2026-07-17

**Co-authors:** Aditi Shinde & Nik Bear Brown — cited in every Manim source annotation.
**Book figures integrated:** Every video has a `BREF` beat (position 1, after cold open) showing
the most relevant chapter SVG figure as a PNG still (`embedded-ai/youtube/images/`).
`integrate_book_images.py` — idempotent, re-runnable. `post_agent_cleanup.sh` — fixes + re-compiles A01–A10.

| list | card# | slug | status | mp4 path | notes |
|------|-------|------|--------|----------|-------|
| A | 01 | claude-liam-doorbell-power-budget | built+BREF | embedded-ai/youtube/claude-liam-doorbell-power-budget/claude-liam-doorbell-power-budget.mp4 | BREF ✓ → ch01-fig02 Wristband Constraint Waterfall |
| A | 02 | claude-liam-duty-cycle-battery | built+BREF | embedded-ai/youtube/claude-liam-duty-cycle-battery/claude-liam-duty-cycle-battery.mp4 | BREF ✓ → ch02-fig03 three duty-cycle current profiles |
| A | 03 | claude-liam-brownout-coin-cell | built+BREF | embedded-ai/youtube/claude-liam-brownout-coin-cell/claude-liam-brownout-coin-cell.mp4 | BREF ✓ → ch07-fig05 annotated current trace |
| A | 04 | claude-liam-nine-weights-convolution | built+BREF | embedded-ai/youtube/claude-liam-nine-weights-convolution/claude-liam-nine-weights-convolution.mp4 | BREF ✓ → ch03-fig03 FC vs conv weight sharing |
| A | 05 | claude-liam-depthwise-split | built+BREF | embedded-ai/youtube/claude-liam-depthwise-split/claude-liam-depthwise-split.mp4 | BREF ✓ → ch03-fig04 depthwise separable conv |
| A | 06 | claude-liam-memory-vs-speed | built+BREF | embedded-ai/youtube/claude-liam-memory-vs-speed/claude-liam-memory-vs-speed.mp4 | BREF ✓ → ch05-fig01 embedded memory hierarchy |
| A | 07 | claude-liam-latency-gap | built+BREF | embedded-ai/youtube/claude-liam-latency-gap/claude-liam-latency-gap.mp4 | BREF ✓ → ch04-fig05 latency waterfall 367ms→45ms |
| A | 08 | claude-liam-activation-memory-crash | built+BREF | embedded-ai/youtube/claude-liam-activation-memory-crash/claude-liam-activation-memory-crash.mp4 | BREF ✓ → ch05-fig05 STM32H743 SRAM overflow |
| A | 09 | claude-liam-lstm-ops | built+BREF | embedded-ai/youtube/claude-liam-lstm-ops/claude-liam-lstm-ops.mp4 | BREF ✓ → ch03-fig01 weights-in-flash activations-in-RAM |
| A | 10 | claude-liam-simd-free-speedup | built+BREF | embedded-ai/youtube/claude-liam-simd-free-speedup/claude-liam-simd-free-speedup.mp4 | BREF ✓ → ch06-fig04 SIMD lane diagram |
| A | 11 | claude-liam-race-to-sleep | built+BREF | embedded-ai/youtube/claude-liam-race-to-sleep/claude-liam-race-to-sleep.mp4 | BREF compiled ✓ → ch07-fig03 race to sleep traces |
| A | 12 | claude-liam-radio-eats-battery | built+BREF | embedded-ai/youtube/claude-liam-radio-eats-battery/claude-liam-radio-eats-battery.mp4 | BREF compiled ✓ → ch07-fig06 battery-life curve |
| A | 13 | claude-liam-cpu-overhead-gap | BUILT | embedded-ai/youtube/claude-liam-cpu-overhead-gap/claude-liam-cpu-overhead-gap.mp4 | 93s · 1.3MB · BREF=ch08-fig01 (human slot) · 2026-07-17 |
| A | 14 | claude-liam-accelerator-routing | BUILT | embedded-ai/youtube/claude-liam-accelerator-routing/claude-liam-accelerator-routing.mp4 | 99s · 1.5MB · BREF=ch08-fig04 (human slot) · 2026-07-17 |
| A | 15 | claude-liam-split-inference | BUILT | embedded-ai/youtube/claude-liam-split-inference/claude-liam-split-inference.mp4 | 100s · 1.7MB · BREF=ch09-fig05 (human slot) · 2026-07-17 |
| A | 16 | claude-liam-async-safety-loop | BUILT | embedded-ai/youtube/claude-liam-async-safety-loop/claude-liam-async-safety-loop.mp4 | 101s · 1.7MB · BREF=ch10-fig05 (human slot) · 2026-07-17 |
| A | 17 | claude-liam-pareto-model-select | BUILT | embedded-ai/youtube/claude-liam-pareto-model-select/claude-liam-pareto-model-select.mp4 | 97s · 1.3MB · BREF=ch11-fig04 (human slot) · 2026-07-17 |
| A | 18 | claude-liam-structured-pruning-wins | BUILT | embedded-ai/youtube/claude-liam-structured-pruning-wins/claude-liam-structured-pruning-wins.mp4 | 98s · 1.6MB · BREF=ch12-fig03 (human slot) · 2026-07-17 |
| A | 19 | claude-liam-quantization-hurts | BUILT | embedded-ai/youtube/claude-liam-quantization-hurts/claude-liam-quantization-hurts.mp4 | 97s · 1.5MB · BREF=ch12-fig01 (human slot) · 2026-07-17 |
| A | 20 | claude-liam-soft-label-lesson | BUILT | embedded-ai/youtube/claude-liam-soft-label-lesson/claude-liam-soft-label-lesson.mp4 | 100s · 1.6MB · BREF=ch12-fig05 (human slot) · 2026-07-17 |
| A | 21 | claude-liam-toolchain-silent-fail | BUILT | embedded-ai/youtube/claude-liam-toolchain-silent-fail/claude-liam-toolchain-silent-fail.mp4 | 102s · 1.8MB · BREF=ch13-fig01 (human slot) · 2026-07-17 |
| A | 22 | claude-liam-architecture-physics | BUILT | embedded-ai/youtube/claude-liam-architecture-physics/claude-liam-architecture-physics.mp4 | 101s · 1.6MB · BREF=ch02-fig04 (human slot) · 2026-07-17 |
| B | 01 | claude-liam-cli-compression-journey | BUILT | embedded-ai/youtube/claude-liam-cli-compression-journey/mp4/claude-liam-cli-compression-journey.mp4 | 3.9 MB, ~140s actual · claude-explainer format · 2026-07-17 |
| B | 02 | claude-liam-cli-int8-mash | BUILT | embedded-ai/youtube/claude-liam-cli-int8-mash/mp4/claude-liam-cli-int8-mash.mp4 | 2.7 MB, ~103s · wide vs narrow range quant |
| B | 03 | claude-liam-cli-pruning-cliff | BUILT | embedded-ai/youtube/claude-liam-cli-pruning-cliff/mp4/claude-liam-cli-pruning-cliff.mp4 | 2.4 MB, ~92s · flat/sweet-spot/cliff curve |
| B | 04 | claude-liam-cli-roofline | BUILT | embedded-ai/youtube/claude-liam-cli-roofline/mp4/claude-liam-cli-roofline.mp4 | 2.7 MB, ~93s · memory-bound→ridge shift |
| B | 05 | claude-liam-cli-battery-life | BUILT | embedded-ai/youtube/claude-liam-cli-battery-life/mp4/claude-liam-cli-battery-life.mp4 | 2.5 MB, ~102s · duty-cycle sweep |
| B | 06 | claude-liam-cli-brownout | BUILT | embedded-ai/youtube/claude-liam-cli-brownout/mp4/claude-liam-cli-brownout.mp4 | 2.2 MB, ~100s · voltage sag trace |
| B | 07 | claude-liam-cli-prune-benchmark | BUILT | embedded-ai/youtube/claude-liam-cli-prune-benchmark/mp4/claude-liam-cli-prune-benchmark.mp4 | 2.3 MB, ~97s · dense vs unstructured vs structured |
| B | 08 | claude-liam-cli-latency-predictor | BUILT | embedded-ai/youtube/claude-liam-cli-latency-predictor/mp4/claude-liam-cli-latency-predictor.mp4 | 3.3 MB, ~101s · four pipeline stages |
| B | 09 | claude-liam-cli-pareto-selector | BUILT | embedded-ai/youtube/claude-liam-cli-pareto-selector/mp4/claude-liam-cli-pareto-selector.mp4 | 2.3 MB, ~94s · scatter → dominated fade → frontier |
| B | 10 | claude-liam-cli-deploy-runner | BUILT | embedded-ai/youtube/claude-liam-cli-deploy-runner/mp4/claude-liam-cli-deploy-runner.mp4 | 3.1 MB, ~99s · pipeline accuracy + bisect |
| B | 11 | claude-liam-cli-distill | BUILT | embedded-ai/youtube/claude-liam-cli-distill/mp4/claude-liam-cli-distill.mp4 | 2.9 MB, ~109s · one-hot vs soft label + temp sweep |
| B | 12 | claude-liam-cli-memory-verdict | BUILT | embedded-ai/youtube/claude-liam-cli-memory-verdict/mp4/claude-liam-cli-memory-verdict.mp4 | 2.4 MB, ~87s · flash/SRAM waterfall + INT8 toggle |
| B | 13 | claude-liam-cli-realtime-verdict | BUILT | embedded-ai/youtube/claude-liam-cli-realtime-verdict/mp4/claude-liam-cli-realtime-verdict.mp4 | 3.3 MB, ~102s · histogram + WCET tail + jitter |
| B | 14 | — | skipped | — | series umbrella, not a standalone video |
