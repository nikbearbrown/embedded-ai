#!/usr/bin/env bash
# post_agent_cleanup.sh — Run AFTER all 4 build agents have completed.
#
# Does three things:
#   1. Fix "Bear Brown)" → "Aditi & Nik Bear Brown)" in ALL scenes.py (catch any
#      the agents wrote after the mid-run fix).
#   2. Re-run integrate_book_images.py to add BREF to any beat_sheets the agents
#      may have overwritten.
#   3. Regenerate audio for any video where beat-BREF.mp3 is missing.
#   4. Re-compile A01–A10 (videos compiled before BREF was available).
#
# Run from books/:
#   bash embedded-ai/youtube/post_agent_cleanup.sh

set -e
cd "$(dirname "$0")/../.."
echo "[cleanup] Working from: $(pwd)"

YOUTUBE=embedded-ai/youtube
ART=brutalist-art/art

# ── Step 1: Fix author attribution in ALL scenes.py ─────────────────────────
echo ""
echo "=== Step 1: Fix author attribution ==="
find "$YOUTUBE"/claude-liam-*/scenes.py -newer /dev/null 2>/dev/null | while read f; do
  if grep -q "(Bear Brown)" "$f" 2>/dev/null; then
    # Only fix the un-prefixed form; "Aditi & Nik Bear Brown)" is already correct
    sed -i '' 's/Embedded AI (Bear Brown)/Embedded AI (Aditi \& Nik Bear Brown)/g' "$f"
    echo "  FIXED: $f"
  fi
done
echo "  Done."

# ── Step 2: Re-run integrate_book_images (idempotent) ──────────────────────
echo ""
echo "=== Step 2: Ensure all beat_sheets have BREF beat ==="
python3 "$YOUTUBE"/integrate_book_images.py 2>&1 | grep -E "✓|✗|⚠|ALREADY|skipped"

# ── Step 3: Generate missing BREF audio ────────────────────────────────────
echo ""
echo "=== Step 3: Generate missing BREF audio ==="
for slug in "$YOUTUBE"/claude-liam-*/; do
  name=$(basename "$slug")
  bref_audio="$slug/mp3/beat-BREF.mp3"
  beat_sheet="$slug/beat_sheet.json"
  if [ ! -f "$beat_sheet" ]; then continue; fi
  # Check if beat_sheet has BREF
  if ! python3 -c "import json; d=json.load(open('$beat_sheet')); exit(0 if any(b['beat_id']=='BREF' for b in d.get('beats',[])) else 1)" 2>/dev/null; then
    continue
  fi
  if [ ! -f "$bref_audio" ]; then
    echo "  Generating BREF audio for $name..."
    python3 brutalist-art/runtime/scripts/generate_audio_kokoro.py --no-gate \
      "$slug" 2>&1 | grep -E "BREF|beat\(s\)|ERROR"
  fi
done
echo "  Done."

# ── Step 4: Re-compile videos that were built before BREF ──────────────────
echo ""
echo "=== Step 4: Re-compile videos that lack BREF in their mp4 ==="
echo "  (Videos A01–A10: compiled before BREF was added)"
echo "  Checking which need re-compile..."

# A video needs re-compile if: mp4 exists AND BREF is in beat_sheet AND
# beat_sheet shows BREF with no 'build' field (not yet compiled with BREF).
RECOMPILE_SLUGS=(
  claude-liam-doorbell-power-budget
  claude-liam-duty-cycle-battery
  claude-liam-brownout-coin-cell
  claude-liam-nine-weights-convolution
  claude-liam-depthwise-split
  claude-liam-memory-vs-speed
  claude-liam-latency-gap
  claude-liam-activation-memory-crash
  claude-liam-lstm-ops
  claude-liam-simd-free-speedup
)

for slug in "${RECOMPILE_SLUGS[@]}"; do
  reel="$YOUTUBE/$slug"
  echo ""
  echo "  Re-compiling $slug..."
  ART_QC=0 ART_FACTS=0 "$ART" run "$reel" 2>&1 | tail -5
done

echo ""
echo "=== post_agent_cleanup.sh complete ==="
echo "Next: review QC contact sheets in each reel, then flip to final with:"
echo "  ART_QC=0 ART_FACTS=0 $ART final $YOUTUBE/<slug>"
