# gallery2.py — cycle through all 10 LED-family faces.
#
# Run with:  mpremote run tools/gallery2.py
#
# 6 frames per design, counter advancing 4 s per frame. The design name is
# printed on the serial console as it comes up, in this order:
#
#   LEDBIG LEDSCROLL LEDWAVE LEDHEART LEDLIFE LEDRAIN LEDEQ
#   LEDSPIRAL LEDFIRE LEDCLOCK

import sys
import time

sys.path.append("/drivers")
sys.path.append("/src")

import display
import designs3

FRAMES = 12

d = display.Display()
cv = d.cv
d.init()

_times = []

for name, fn in designs3.DESIGNS:
    print("=== %s" % name)
    for f in range(FRAMES):
        fn(cv, 0, f * 4, f)
        t0 = time.ticks_ms()
        if f == 0:
            d.base()
        else:
            d.partial()
        _times.append(time.ticks_diff(time.ticks_ms(), t0))

print("frames: %d  avg: %d ms" % (len(_times), sum(_times) // len(_times)))
