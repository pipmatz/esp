# gallery.py — cycle through the candidate timer faces.
#
# Run with:  mpremote run tools/gallery.py
#
# Each design gets 8 frames, the counter advancing 4 s per frame, so you see
# it animate rather than as a static image. The design name is printed on the
# serial console as it comes up.

import sys
import time

sys.path.append("/drivers")
sys.path.append("/src")

import display
import designs

FRAMES = 8

d = display.Display()
cv = d.cv
d.init()

_times = []

for name, fn in designs.DESIGNS:
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
