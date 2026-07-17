#!/usr/bin/env python3
"""
integrate_book_images.py — Inject textbook SVG figures into embedded-ai claude-liam reels.

For each video, converts the most relevant chapter figure(s) to PNG, places them in
media/BREF.png, and inserts a "BREF" beat at position 1 (after B00 cold open).

Run AFTER all agents have finished building beat_sheets.
Usage:
    cd /path/to/books
    python3 embedded-ai/youtube/integrate_book_images.py [--dry-run] [--slug <slug>]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Figure → video mapping
# Each entry: slug → {fig: primary figure path (relative to images/), narration: ~5s line}
# ──────────────────────────────────────────────────────────────────────────────
IMAGES_DIR = Path("embedded-ai/youtube/images")
YOUTUBE_DIR = Path("embedded-ai/youtube")

FIGURE_MAP = {
    # ── Part A: concept explainers ──────────────────────────────────────────
    "claude-liam-doorbell-power-budget": {
        "fig": "chapter-01-when-ai-meets-constrained-hardware-fig-02.svg",
        "narration": "The textbook puts it in three bars: memory passes, latency passes, power fails. That single red bar is why the doorbell died.",
    },
    "claude-liam-duty-cycle-battery": {
        "fig": "chapter-02-embedded-constraints-as-design-variables-fig-03.svg",
        "narration": "Here are three nRF52840 current profiles from the book — same chip, three duty cycles, three completely different battery lives.",
    },
    "claude-liam-brownout-coin-cell": {
        "fig": "chapter-07-power-and-energy-fig-05.svg",
        "narration": "This annotated current trace is from the book — every phase of one duty cycle: sleep floor, wake-up spike, inference peak, settle, back to sleep.",
    },
    "claude-liam-nine-weights-convolution": {
        "fig": "chapter-03-ml-for-embedded-engineers-fig-03.svg",
        "narration": "The book's comparison says it plainly: nineteen million weights in a fully-connected layer, versus weight sharing in a convolution. Nine parameters, reused everywhere.",
    },
    "claude-liam-depthwise-split": {
        "fig": "chapter-03-ml-for-embedded-engineers-fig-04.svg",
        "narration": "From the textbook: standard convolution on top — eighteen thousand multiplications per output pixel. Depthwise separable below — roughly nine times cheaper.",
    },
    "claude-liam-memory-vs-speed": {
        "fig": "chapter-05-memory-fig-01.svg",
        "narration": "This is the embedded memory hierarchy from the book — registers, SRAM, flash, external storage. Speed drops at every level; capacity climbs. Weights live in flash; activations fight for SRAM.",
    },
    "claude-liam-latency-gap": {
        "fig": "chapter-04-inference-mechanics-fig-05.svg",
        "narration": "The book's latency waterfall: three hundred sixty-seven milliseconds predicted, twelve hundred on first deployment, forty-five after profiling. The gap between prediction and reality is the story.",
    },
    "claude-liam-activation-memory-crash": {
        "fig": "chapter-05-memory-fig-05.svg",
        "narration": "From the book: the STM32H743 SRAM budget after one arena bump — you can see exactly where inference overflows the one-megabyte wall and the system crashes.",
    },
    "claude-liam-lstm-ops": {
        "fig": "chapter-03-ml-for-embedded-engineers-fig-01.svg",
        "narration": "The book's memory map: weights live in flash, activations fight for SRAM. For an LSTM every time-step reuses weights but allocates new hidden-state activations.",
    },
    "claude-liam-simd-free-speedup": {
        "fig": "chapter-06-compute-fig-04.svg",
        "narration": "The book's SIMD diagram: one thirty-two-bit register split into four eight-bit lanes. Four multiply-add instructions collapse into one. Same clock, four times the throughput.",
    },
    "claude-liam-race-to-sleep": {
        "fig": "chapter-07-power-and-energy-fig-03.svg",
        "narration": "From the book: two overlaid current traces. The sixty-four megahertz clock draws more while active but finishes in less than half the time — lower energy total. Race to sleep.",
    },
    "claude-liam-radio-eats-battery": {
        "fig": "chapter-07-power-and-energy-fig-06.svg",
        "narration": "This is the book's battery-life curve — inference period on the x-axis, months on the y-axis. See where the curve flattens? That's where the radio becomes the ceiling, not inference.",
    },
    "claude-liam-cpu-overhead-gap": {
        "fig": "chapter-08-hardware-for-ai-fig-01.svg",
        "narration": "The book's side-by-side: a Cortex-M7 CPU versus a dedicated NPU on the same hundred-twenty-eight by one-twenty-eight matmul. The CPU spends most cycles on overhead. The NPU almost none.",
    },
    "claude-liam-accelerator-routing": {
        "fig": "chapter-08-hardware-for-ai-fig-04.svg",
        "narration": "From the textbook: a Cortex-M55 host and an Ethos-U55 NPU sharing an SRAM pool. The supported ops route to the NPU. Everything else falls back to the CPU. That handoff is the routing problem.",
    },
    "claude-liam-split-inference": {
        "fig": "chapter-09-communication-edge-cloud-fig-05.svg",
        "narration": "The book's MobileNetV2 split-inference diagram: activation tensor sizes annotated at each layer boundary. Find the cut where activations are smaller than your radio budget.",
    },
    "claude-liam-async-safety-loop": {
        "fig": "chapter-10-real-time-ai-fig-05.svg",
        "narration": "From the book: three parallel timelines on a CNC mill. The one-kilohertz control loop never touches the AI. The AI runs async, updates a shared probability register, and stays off the critical path.",
    },
    "claude-liam-pareto-model-select": {
        "fig": "chapter-11-model-selection-fig-04.svg",
        "narration": "The book's Pareto scatter: six face-detection candidates on latency versus accuracy. Two are dominated — strictly worse on both axes. The frontier is the only honest shortlist.",
    },
    "claude-liam-structured-pruning-wins": {
        "fig": "chapter-12-model-optimization-fig-03.svg",
        "narration": "The book's pruning comparison: unstructured on the left, scattered zeros the hardware ignores. Structured on the right — whole channels gone, the matrix actually shrinks.",
    },
    "claude-liam-quantization-hurts": {
        "fig": "chapter-12-model-optimization-fig-01.svg",
        "narration": "From the book: two number lines. Top — weights spread across the full int8 range, clean mapping. Bottom — activations crammed into a tiny range, dozens of float values collapsing onto the same integer bin.",
    },
    "claude-liam-soft-label-lesson": {
        "fig": "chapter-12-model-optimization-fig-05.svg",
        "narration": "The book's distillation pipeline: one image into the large teacher, same image into the small student. The soft-label probability distribution is the signal the student learns from — not just the hard label.",
    },
    "claude-liam-toolchain-silent-fail": {
        "fig": "chapter-13-tinyml-toolchains-fig-01.svg",
        "narration": "From the book: the six-step deployment pipeline with dominant failure modes annotated at each stage. Training passes. Conversion passes. The silent failure often lives in optimize or compile.",
    },
    "claude-liam-architecture-physics": {
        "fig": "chapter-02-embedded-constraints-as-design-variables-fig-04.svg",
        "narration": "The book's four-constraint coupling diagram: memory, compute, power, real-time at the four corners. Every edge is a coupling — tighten one constraint and it pulls on two others.",
    },

    # ── Part B: CLI explainers ───────────────────────────────────────────────
    "claude-liam-cli-compression-journey": {
        "fig": "chapter-12-model-optimization-fig-06.svg",
        "narration": "The book's MobileNetV2-0.5 case study — this is the exact model we're compressing. Flash, SRAM, latency, and accuracy tracked across four optimization steps.",
    },
    "claude-liam-cli-int8-mash": {
        "fig": "chapter-12-model-optimization-fig-01.svg",
        "narration": "From the textbook: the quantization number-line diagram. That bottom strip — where a huge float range crushes into a handful of integer bins — is exactly what our CLI script detects.",
    },
    "claude-liam-cli-pruning-cliff": {
        "fig": "chapter-12-model-optimization-fig-04.svg",
        "narration": "The book's accuracy-versus-pruning-rate curve. The cliff past seventy percent is real — our CLI script finds where the curve goes steep before you commit to a pruning target.",
    },
    "claude-liam-cli-roofline": {
        "fig": "chapter-06-compute-fig-02.svg",
        "narration": "From the book: the roofline model — arithmetic intensity on x, achievable performance on y. Our script computes where your model sits on this plot and tells you which roof you're hitting.",
    },
    "claude-liam-cli-battery-life": {
        "fig": "chapter-07-power-and-energy-fig-06.svg",
        "narration": "The book's battery-life curve. Our CLI script predicts where your system lands on this curve — and whether inference frequency or radio transmission is the binding constraint.",
    },
    "claude-liam-cli-brownout": {
        "fig": "chapter-07-power-and-energy-fig-05.svg",
        "narration": "From the textbook: the annotated current trace. Our brownout detector looks for exactly the pattern in this figure — a peak current spike that dips the rail below the reset threshold.",
    },
    "claude-liam-cli-prune-benchmark": {
        "fig": "chapter-12-model-optimization-fig-04.svg",
        "narration": "The book's pruning-rate versus accuracy chart. Our benchmark script sweeps this curve automatically — finding the knee point where structured pruning starts costing accuracy.",
    },
    "claude-liam-cli-latency-predictor": {
        "fig": "chapter-04-inference-mechanics-fig-05.svg",
        "narration": "The book's latency waterfall — predicted versus deployed. Our CLI predictor closes that gap by accounting for memory access patterns, not just arithmetic.",
    },
    "claude-liam-cli-pareto-selector": {
        "fig": "chapter-11-model-selection-fig-04.svg",
        "narration": "From the book: the Pareto frontier for face-detection candidates. Our CLI selector builds this plot automatically for any model family you give it.",
    },
    "claude-liam-cli-deploy-runner": {
        "fig": "chapter-13-tinyml-toolchains-fig-01.svg",
        "narration": "The book's six-step deployment pipeline. Our deploy runner automates steps three through five — optimize, compile, verify — and flags the dominant failure mode at each gate.",
    },
    "claude-liam-cli-distill": {
        "fig": "chapter-12-model-optimization-fig-05.svg",
        "narration": "From the textbook: the distillation pipeline. Our CLI script sets up the teacher-student training loop shown here, with soft-label temperature as a tunable parameter.",
    },
    "claude-liam-cli-memory-verdict": {
        "fig": "chapter-05-memory-fig-05.svg",
        "narration": "The book's SRAM overflow diagram. Our memory-verdict script tells you exactly how much headroom you have — or how far you're over — before you flash the device.",
    },
    "claude-liam-cli-realtime-verdict": {
        "fig": "chapter-10-real-time-ai-fig-01.svg",
        "narration": "From the book: hard, firm, and soft real-time compared on deadline tolerance and consequence of miss. Our verdict script classifies your system and checks whether the AI fits the timing envelope.",
    },
}


def convert_svg_to_png(svg_path: Path, png_path: Path, width: int = 1440) -> bool:
    """Convert SVG to PNG using inkscape or imagemagick."""
    png_path.parent.mkdir(parents=True, exist_ok=True)

    # Try inkscape first (better SVG rendering)
    try:
        result = subprocess.run(
            ["inkscape", "--export-type=png", f"--export-width={width}",
             f"--export-filename={png_path}", str(svg_path)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and png_path.exists():
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fall back to imagemagick
    try:
        result = subprocess.run(
            ["magick", "-density", "150", "-background", "white",
             "-flatten", str(svg_path), str(png_path)],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and png_path.exists():
            return True
        # Try legacy convert
        result = subprocess.run(
            ["convert", "-density", "150", "-background", "white",
             "-flatten", str(svg_path), str(png_path)],
            capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0 and png_path.exists()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return False


def insert_bref_beat(beat_sheet: dict, narration: str) -> bool:
    """Insert BREF beat at position 1 (after B00 cold open). Returns True if inserted."""
    beats = beat_sheet.get("beats", [])

    # Check if already present
    if any(b["beat_id"] == "BREF" for b in beats):
        return False  # already inserted

    bref_beat = {
        "beat_id": "BREF",
        "act": "TEXTBOOK FIGURE",
        "narration_text": narration,
        "shot": {
            "type": "GRAPHIC",
            "source": "media",
            "motion": "fade",
            "file": "BREF.png"
        },
        "estimated_duration_s": 5,
    }

    # Insert after B00 (index 0), or at index 1
    insert_idx = 1
    if beats and beats[0].get("beat_id") == "B00":
        insert_idx = 1

    beats.insert(insert_idx, bref_beat)
    beat_sheet["beats"] = beats
    return True


def process_slug(slug: str, dry_run: bool = False) -> dict:
    """Process one video slug. Returns status dict."""
    mapping = FIGURE_MAP.get(slug)
    if not mapping:
        return {"slug": slug, "status": "NO_MAPPING"}

    reel_dir = YOUTUBE_DIR / slug
    if not reel_dir.exists():
        return {"slug": slug, "status": "NO_REEL_DIR"}

    beat_sheet_path = reel_dir / "beat_sheet.json"
    if not beat_sheet_path.exists():
        return {"slug": slug, "status": "NO_BEAT_SHEET"}

    svg_path = IMAGES_DIR / mapping["fig"]
    if not svg_path.exists():
        return {"slug": slug, "status": f"SVG_MISSING: {mapping['fig']}"}

    png_dest = reel_dir / "media" / "BREF.png"
    narration = mapping["narration"]

    print(f"[{slug}]")
    print(f"  fig: {mapping['fig']}")

    if dry_run:
        print(f"  → would convert SVG → {png_dest}")
        print(f"  → would insert BREF beat: \"{narration[:60]}...\"")
        return {"slug": slug, "status": "DRY_RUN_OK"}

    # Convert SVG → PNG
    ok = convert_svg_to_png(svg_path, png_dest)
    if not ok:
        print(f"  ✗ SVG conversion failed")
        return {"slug": slug, "status": "SVG_CONVERT_FAIL"}
    print(f"  ✓ PNG → {png_dest}")

    # Update beat_sheet
    with open(beat_sheet_path) as f:
        sheet = json.load(f)

    inserted = insert_bref_beat(sheet, narration)
    if not inserted:
        print(f"  ⚠ BREF beat already present — skipping beat_sheet update")
        return {"slug": slug, "status": "ALREADY_DONE"}

    with open(beat_sheet_path, "w") as f:
        json.dump(sheet, f, indent=1, ensure_ascii=False)
    print(f"  ✓ beat_sheet updated (BREF inserted at position 1)")

    return {"slug": slug, "status": "OK"}


def main():
    parser = argparse.ArgumentParser(description="Integrate book SVG figures into claude-liam reels")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without writing files")
    parser.add_argument("--slug", help="Process only this slug (default: all)")
    args = parser.parse_args()

    if not IMAGES_DIR.exists():
        sys.exit(f"Images dir not found: {IMAGES_DIR}")

    slugs = [args.slug] if args.slug else list(FIGURE_MAP.keys())
    results = []
    for slug in slugs:
        r = process_slug(slug, dry_run=args.dry_run)
        results.append(r)
        print()

    ok = [r for r in results if r["status"] in ("OK", "DRY_RUN_OK")]
    skip = [r for r in results if r["status"] not in ("OK", "DRY_RUN_OK", "ALREADY_DONE")]
    already = [r for r in results if r["status"] == "ALREADY_DONE"]

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Done: {len(ok)} processed, "
          f"{len(already)} already done, {len(skip)} skipped/failed")
    for r in skip:
        print(f"  SKIP {r['slug']}: {r['status']}")

    if not args.dry_run and ok:
        print()
        print("Next step: regenerate audio for BREF beats only isn't directly supported,")
        print("so re-run full audio generation per reel (Kokoro is free):")
        print()
        print("  cd /path/to/books")
        print("  SLUGS=(", " ".join(r['slug'] for r in ok), ")")
        print("  for slug in $SLUGS; do")
        print("    python3 brutalist-art/runtime/scripts/generate_audio_kokoro.py --no-gate \\")
        print("      embedded-ai/youtube/$slug")
        print("  done")


if __name__ == "__main__":
    main()
