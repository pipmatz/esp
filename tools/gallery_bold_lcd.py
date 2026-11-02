# gallery_bold_lcd.py — BOLD and LCD side by side in time.
# Run with:  mpremote run tools/gallery_bold_lcd.py

import sys
import time

sys.path.append("/drivers")
sys.path.append("/src")

import display
import astro
import digitfonts

FRAMES = 16

d = display.Display()
cv = d.cv
d.init()

for name, font, scale in (("BOLD", digitfonts.BOLD, 6),
                          ("LCD", digitfonts.LCD, 6)):
    print("=== %s" % name)
    for f in range(FRAMES):
        astro.astro_float_inv(cv, 0, f, f, font, scale)
        if f == 0:
            d.base()
        else:
            d.partial()

print("done")
