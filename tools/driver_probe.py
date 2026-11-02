# driver_probe.py — milestone 3: identify the controller and the orientation.
#
# Run with:  mpremote run tools/driver_probe.py
#
# Draws an asymmetric pattern in the panel's NATIVE portrait orientation
# (122 wide x 250 tall). Report back:
#
#   1. Is the image clean, or garbage / blank / half-filled?
#   2. Which corner has the big black square?
#   3. Do the corner square and the "V4" text read the right way up?
#
# Clean image  -> SSD1680, driver is correct.
# Garbage      -> try epd2in13_V3 (UC8151D).

import sys
import time

sys.path.append("/drivers")

import framebuf
import epd2in13_V4 as drv

W = drv.EPD_WIDTH   # 122
H = drv.EPD_HEIGHT  # 250

# MONO_HLSB: 1 bit per pixel, LSB first. Verified empirically on this panel
# (see driver_probe2.py): MSB-first comes out unreadable and mirror-ish.
buf = bytearray(drv.BUFFER_SIZE)
fb = framebuf.FrameBuffer(buf, W, H, framebuf.MONO_HLSB)

WHITE = 1
BLACK = 0

fb.fill(WHITE)

# 1 px border so we can see the exact panel edges
fb.rect(0, 0, W, H, BLACK)

# Asymmetric landmarks: 24x24 solid blocks in two opposite corners
fb.fill_rect(0, 0, 24, 24, BLACK)              # top-left
fb.fill_rect(W - 24, H - 24, 24, 24, BLACK)    # bottom-right

# Cross-hairs through the middle
fb.hline(0, H // 2, W, BLACK)
fb.vline(W // 2, 0, H, BLACK)

# Text: framebuf's built-in 8x8 font, no scaling available, so draw twice
# at different offsets to make it legible.
fb.text("V4", 30, 40, BLACK)
fb.text("122x250", 30, 60, BLACK)
fb.text("SSD1680", 30, 80, BLACK)
fb.text("top", 30, 100, BLACK)

epd = drv.EPD()
epd.init()

t0 = time.ticks_ms()
epd.display(buf)
t1 = time.ticks_ms()

print("display() took %d ms" % time.ticks_diff(t1, t0))

# Second pass with the inverse, to prove RAM is being fully rewritten
fb.fill(BLACK)
fb.rect(0, 0, W, H, WHITE)
fb.fill_rect(0, 0, 24, 24, WHITE)
fb.fill_rect(W - 24, H - 24, 24, 24, WHITE)
fb.text("INVERSE", 30, 120, WHITE)

time.sleep(2)
t0 = time.ticks_ms()
epd.display(buf)
t1 = time.ticks_ms()
print("inverse display() took %d ms" % time.ticks_diff(t1, t0))

print("probe done")
