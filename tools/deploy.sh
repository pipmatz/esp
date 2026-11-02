#!/usr/bin/env bash
# Copy drivers/ and src/ onto the board.
#
# The app lives at /src, with src/main.py deployed as /main.py so it runs on
# boot. boot.py is left alone.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${1:-/dev/cu.usbmodem1101}"
MP=".venv/bin/mpremote connect $PORT"

$MP fs mkdir :/drivers 2>/dev/null || true
$MP fs mkdir :/src 2>/dev/null || true

$MP fs cp drivers/epdconfig.py :/drivers/epdconfig.py
$MP fs cp drivers/epd2in13_V4.py :/drivers/epd2in13_V4.py

for f in config canvas display font5x7 gfx digitfonts sprites \
         sessions sensor button state astro space main; do
  $MP fs cp "src/$f.py" ":/src/$f.py"
done

# entry point
$MP fs cp src/main.py :/main.py

echo "deployed to $PORT"
