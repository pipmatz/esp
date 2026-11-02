# probe_landscape.py — verify the landscape rotation and text rendering.
#
# Hold the panel so it is WIDE (250 px across, 122 px tall). The content
# should read normally, not mirrored and not upside down:
#
#   TOP LEFT      <- top-left corner
#   BOTTOM LEFT   <- bottom-left corner
#   a black square in the top-right corner
#   big digits 0123 on the right half
#
# If it is upside down, set ROTATION = "ccw" in src/config.py.
# If the text is mirrored, the bit order is wrong (should be MONO_HLSB).

import sys
import time

sys.path.append("/drivers")
sys.path.append("/src")

import epd2in13_V4 as drv
import config
import canvas

buf = bytearray(drv.BUFFER_SIZE)
cv = canvas.Canvas(buf)

WHITE = 1
BLACK = 0

cv.fill(WHITE)
cv.rect(0, 0, cv.w, cv.h, BLACK)

# corner labels
cv.text("TOP LEFT", 4, 4, BLACK, 1)
cv.text("BOTTOM LEFT", 4, cv.h - 12, BLACK, 1)

# asymmetric marker: solid square in the top-right corner
cv.fill_rect(cv.w - 20, 0, 20, 20, BLACK)

# big digits on the right half
cv.text("0123", 150, 40, BLACK, 3)

# a 1 px frame around the right-hand text column, to check the split at x=122
cv.rect(122, 0, cv.w - 122, cv.h, BLACK)

epd = drv.EPD()
epd.init()

t0 = time.ticks_ms()
epd.display(buf)
print("display() took %d ms" % time.ticks_diff(time.ticks_ms(), t0))
print("view %dx%d, rotation=%s" % (cv.w, cv.h, cv.rot))
