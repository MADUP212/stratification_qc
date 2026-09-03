#!/usr/bin/env bash
# Produit Gabarit/gabarit_snowballing.pdf SANS LaTeX : tricotage du Rmd en HTML (R + pandoc) puis impression en PDF
# avec Chrome/Chromium headless (en-tête, numéros de page et police définis dans Gabarit/gabarit_snowballing.css).
# Usage : bash Scripts/imprimer_gabarit_pdf.sh [chemin/vers/chromium]
set -euo pipefail
cd "$(dirname "$0")/../Gabarit"
CHROME="${1:-${CHROME:-$(command -v chromium || command -v chromium-browser || command -v google-chrome || echo /opt/pw-browsers/chromium)}}"
export LANG=C.UTF-8 LC_ALL=C.UTF-8
Rscript -e 'rmarkdown::render("gabarit_snowballing.Rmd", output_format = "html_document", output_file = "gabarit_snowballing.html", quiet = TRUE)'
"$CHROME" --headless --no-sandbox --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$(pwd)/gabarit_snowballing.pdf" "file://$(pwd)/gabarit_snowballing.html" 2>/dev/null
echo "PDF écrit : $(pwd)/gabarit_snowballing.pdf"
