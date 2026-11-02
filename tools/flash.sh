#!/usr/bin/env bash
# Erase flash and install MicroPython (SPIRAM_OCT build for the N16R8 module).
#
# The board must be in download mode first:
#   hold BOOT -> tap RESET -> release BOOT
# A board running firmware that owns the USB peripheral cannot be reached by
# esptool until you do this.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${1:-/dev/cu.usbmodem1234561}"
FW="$(ls firmware/ESP32_GENERIC_S3-SPIRAM_OCT-*.bin 2>/dev/null | tail -1)"

if [ -z "$FW" ]; then
  echo "No firmware found in firmware/. Download one first." >&2
  exit 1
fi

echo "port     : $PORT"
echo "firmware : $FW"
echo

.venv/bin/esptool --chip esp32s3 -p "$PORT" -b 460800 erase-flash
.venv/bin/esptool --chip esp32s3 -p "$PORT" -b 460800 write-flash -z 0 "$FW"

echo
echo "Done. The board reboots into MicroPython and will re-enumerate."
echo "Check with: .venv/bin/mpremote connect list"
