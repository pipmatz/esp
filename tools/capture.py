# capture.py — 30 s of sensor data, logged as a sample list.
#
# Run with:  mpremote run tools/capture.py
#
# Samples the rolling-window edge count as fast as it can and refreshes a live
# readout on the panel every ~2 s so you can see it while you work.

import sys
import time

sys.path.append("/drivers")
sys.path.append("/src")

import config
import display
import sensor
import font5x7 as f7

SECONDS = 30

d = display.Display()
d.init()
cv = d.cv

s = sensor.Sensor()
vals = []
start = time.ticks_ms()
last_draw = -9999
peak = 0

while True:
    now = time.ticks_ms()
    if time.ticks_diff(now, start) >= SECONDS * 1000:
        break

    r = s.recent()
    vals.append(r)
    if r > peak:
        peak = r

    if time.ticks_diff(now, last_draw) > 2000:
        cv.fill(0)
        f7.draw(cv, "EDGES", 8, 6, 2, 1)
        f7.draw(cv, "%02d" % r, 8, 26, 6, 1)
        f7.draw(cv, "PEAK %02d" % peak, 120, 30, 2, 1)
        f7.draw(cv, "TRIG %02d" % config.SENSOR_MIN_EDGES, 120, 50, 2, 1)
        w = r // 2
        if w > 240:
            w = 240
        cv.fill_rect(8, 96, w, 12, 1)
        cv.vline(8 + config.SENSOR_MIN_EDGES * 2, 92, 20, 1)
        d.partial()
        last_draw = time.ticks_ms()

    time.sleep_ms(80)

print("samples=%d peak=%d" % (len(vals), peak))
print("DATA:" + ",".join(str(v) for v in vals))
