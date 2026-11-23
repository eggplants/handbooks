#!/usr/bin/env bash
# Render SVG figures to PNG so that they can be looked at with the Read tool.
# Checks that each file is well-formed XML first, then draws it at the size of its viewBox.
#
#   render_svg.sh OUT_DIR src/images/*.svg
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "usage: $0 OUT_DIR FILE.svg..." >&2
  exit 2
fi
out=$1
shift
mkdir -p "$out"

chrome=""
for c in google-chrome google-chrome-stable chromium chromium-browser; do
  if command -v "$c" >/dev/null 2>&1; then
    chrome=$c
    break
  fi
done

status=0
for svg in "$@"; do
  name=$(basename "$svg" .svg)
  if ! size=$(python3 - "$svg" <<'EOF'
import re, sys
from xml.dom import minidom
el = minidom.parse(sys.argv[1]).documentElement
vb = el.getAttribute("viewBox").replace(",", " ").split()
w, h = (vb[2], vb[3]) if len(vb) == 4 else (el.getAttribute("width") or "720", el.getAttribute("height") or "400")
print(round(float(re.sub(r"[a-z]+$", "", w))), round(float(re.sub(r"[a-z]+$", "", h))))
EOF
  ); then
    echo "NG   $svg: not well-formed XML" >&2
    status=1
    continue
  fi
  read -r w h <<<"$size"
  png="$out/$name.png"
  if [ -n "$chrome" ]; then
    timeout 60 "$chrome" --headless=new --disable-gpu --no-sandbox --hide-scrollbars \
      --window-size="$w,$h" --screenshot="$png" "file://$(realpath "$svg")" >/dev/null 2>&1 || true
  elif command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert -w "$w" -h "$h" -o "$png" "$svg"
  elif command -v magick >/dev/null 2>&1; then
    magick -background none -density 96 "$svg" "$png"
  else
    echo "no renderer found (google-chrome, chromium, rsvg-convert or magick)" >&2
    exit 1
  fi
  if [ -s "$png" ]; then
    echo "ok   $png (${w}x${h})"
  else
    echo "NG   $svg: rendering failed" >&2
    status=1
  fi
done
exit $status
