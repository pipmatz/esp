# gallery_fonts.py — same astronaut composition, eight different digit faces.
#
# Run with:  mpremote run tools/gallery_fonts.py
#
# Order: PIXEL BOLD ROUND STENCIL SERIF CONDENSED SEG7 LCD
# 6 frames each, seconds 00..20.

import sys
import time

sys.path.append("/drivers")
sys.path.append("/src")

import display
import astro
import digitfonts

FRAMES = 6

d = display.Display()
cv = d.cv
d.init()

_times = []

for name, font, scale in digitfonts.FONTS:
    print("=== %s" % name)
    for f in range(FRAMES):
        astro.astro_float_inv(cv, 0, f * 4, f, font, scale)
        t0 = time.ticks_ms()
        if f == 0:
            d.base()
        else:
            d.partial()
        _times.append(time.ticks_diff(time.ticks_ms(), t0))

print("frames: %d  avg: %d ms" % (len(_times), sum(_times) // len(_times)))
