#!/bin/bash
set -e
BOOK_SLUG="trust-the-teacher"
METADATA="metadata.yaml"
OUTPUT_DIR="output"
mkdir -p "$OUTPUT_DIR"

# EPUB (primary — upload this to KDP)
pandoc chapters/*.md \
  --metadata-file="$METADATA" \
  --resource-path=".:chapters" \
  --from markdown \
  --to epub3 \
  --epub-cover-image=cover.jpg \
  --css=styles/kindle.css \
  --css=styles/kindle-book.css \
  --toc --toc-depth=2 \
  --output="$OUTPUT_DIR/$BOOK_SLUG.epub"

# HTML (proofing — mirrors EPUB cascade exactly)
pandoc chapters/*.md \
  --metadata-file="$METADATA" \
  --resource-path=".:chapters" \
  --from markdown \
  --to html5 \
  --standalone \
  --css=styles/kindle.css \
  --css=styles/kindle-book.css \
  --toc \
  --output="$OUTPUT_DIR/$BOOK_SLUG.html"

# PDF (LinkedIn / sharing — requires either weasyprint or xelatex)
if command -v weasyprint &> /dev/null; then
  pandoc chapters/*.md \
    --metadata-file="$METADATA" \
    --resource-path=".:chapters" \
    --from markdown \
    --to html5 \
    --standalone \
    --embed-resources \
    --css=styles/kindle.css \
    --css=styles/kindle-book.css \
    --toc \
    --output="$OUTPUT_DIR/$BOOK_SLUG-pdf-intermediate.html"
  weasyprint \
    "$OUTPUT_DIR/$BOOK_SLUG-pdf-intermediate.html" \
    "$OUTPUT_DIR/$BOOK_SLUG.pdf"
  rm "$OUTPUT_DIR/$BOOK_SLUG-pdf-intermediate.html"
  echo "Built (weasyprint): $OUTPUT_DIR/$BOOK_SLUG.pdf"
elif command -v xelatex &> /dev/null; then
  pandoc chapters/*.md \
    --metadata-file="$METADATA" \
    --resource-path=".:chapters" \
    --from markdown \
    --pdf-engine=xelatex \
    --variable mainfont="Georgia" \
    --variable fontsize=11pt \
    --variable geometry="margin=1.25in" \
    --variable linestretch=1.4 \
    --toc --toc-depth=2 \
    --output="$OUTPUT_DIR/$BOOK_SLUG.pdf"
  echo "Built (xelatex): $OUTPUT_DIR/$BOOK_SLUG.pdf"
else
  echo "WARNING: No PDF engine found. Install weasyprint (brew install weasyprint) or xelatex (texlive)."
  echo "Skipping PDF build."
fi

echo "Built: $OUTPUT_DIR/$BOOK_SLUG.epub"
echo "Built: $OUTPUT_DIR/$BOOK_SLUG.html"