#!/usr/bin/env bash
# Set the board's RTC from this machine's clock.
#
# The ESP32-S3 has no battery-backed clock, so after every power cycle the
# time resets to 2000-01-01 until something sets it. Without WiFi/NTP this is
# the simplest way to get a real timestamp on screen.
#
#   ./tools/settime.sh [port]
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${1:-/dev/cu.usbmodem1101}"
read -r Y M D H MI S <<< "$(date '+%Y %m %d %H %M %S')"

# strip leading zeros: "08" and "09" are invalid integer literals in Python 3
M=$((10#$M))
D=$((10#$D))
H=$((10#$H))
MI=$((10#$MI))
S=$((10#$S))

.venv/bin/mpremote connect "$PORT" exec "
import machine, time
machine.RTC().datetime(($Y, $M, $D, 0, $H, $MI, $S, 0))
t = time.localtime()
print('rtc set to %04d-%02d-%02d %02d:%02d:%02d' % (t[0], t[1], t[2], t[3], t[4], t[5]))
"
