# tune_sensor.py — live on-screen readout of the vibration sensor.
#
# Run with:  mpremote run tools/tune_sensor.py
#
# Shows, on the panel:
#   big number  = falling edges in the last SENSOR_WINDOW_MS
#   PEAK        = highest value seen so far
#   bar         = the current value, with a marker at SENSOR_MIN_EDGES
#
# Tap the portafilter a few times, then run the pump. The knock should stay
# below the marker, the pump well above it.

import sys
import time

sys.path.append("/drivers")
sys.path.append("/src")

import config
import display
import sensor
import font5x7 as f7

SECONDS = 90

d = display.Display()
d.init()
cv = d.cv

s = sensor.Sensor()
peak = 0
knock_peak = 0
start = time.ticks_ms()

while time.ticks_diff(time.ticks_ms(), start) < SECONDS * 1000:
    r = s.recent()
    if r > peak:
        peak = r

    cv.fill(0)
    f7.draw(cv, "EDGES", 8, 6, 2, 1)
    f7.draw(cv, "%02d" % r, 8, 26, 6, 1)
    f7.draw(cv, "PEAK %02d" % peak, 120, 30, 2, 1)
    f7.draw(cv, "TRIG %02d" % config.SENSOR_MIN_EDGES, 120, 50, 2, 1)

    # bar, 2 px per edge, capped at the panel width
    w = r * 2
    if w > 240:
        w = 240
    cv.fill_rect(8, 96, w, 12, 1)

    # threshold marker
    tx = 8 + config.SENSOR_MIN_EDGES * 2
    cv.vline(tx, 92, 20, 1)

    d.partial()

print("peak over %ds: %d edges (trigger is %d)" % (SECONDS, peak,
                                                   config.SENSOR_MIN_EDGES))
