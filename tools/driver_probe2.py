# driver_probe2.py — figure out bit order / mirroring / polarity in ONE refresh.
#
# The panel is split into 5 horizontal bands, 50 rows each. Every band holds
# the same content ("TEST" + two squares), but each band is pre-transformed
# differently before being sent:
#
#   band 0 : as-is
#   band 1 : every byte bit-reversed      (panel expects LSB-first)
#   band 2 : image mirrored horizontally  (panel scans X the other way)
#   band 3 : bit-reversed + mirrored
#   band 4 : colours inverted             (panel's 1 means black)
#
# Report which band(s) look CORRECT. Bands are counted from the top edge,
# 0..4. If none look right, the controller is probably not an SSD1680 and we
# switch to the epd2in13_V3 (UC8151D) driver.

import sys
import time

sys.path.append("/drivers")

import framebuf
import epd2in13_V4 as drv

W = drv.EPD_WIDTH    # 122
H = drv.EPD_HEIGHT   # 250
BAND_H = 50
ROW_BYTES = (W + 7) // 8   # 16

# bit-reversal lookup table (MicroPython has no negative-step slices)
REV = bytearray(256)
for _i in range(256):
    _r = 0
    _v = _i
    for _ in range(8):
        _r = (_r << 1) | (_v & 1)
        _v >>= 1
    REV[_i] = _r
REV = bytes(REV)


def build_band(label, mode):
    bb = bytearray(ROW_BYTES * BAND_H)
    bfb = framebuf.FrameBuffer(bb, W, BAND_H, framebuf.MONO_HMSB)
    bfb.fill(1)                              # white
    bfb.rect(0, 0, W, BAND_H, 0)             # black border
    bfb.text(label, 4, 4, 0)
    bfb.fill_rect(4, 22, 12, 12, 0)          # square on the left
    bfb.fill_rect(W - 16, 22, 12, 12, 0)     # square on the right
    bfb.text("TEST", 40, 24, 0)

    if mode == 0:
        return bb
    if mode == 1:
        return bytearray(REV[b] for b in bb)
    if mode == 2:
        out = bytearray(len(bb))
        for y in range(BAND_H):
            base = y * ROW_BYTES
            for x in range(W):
                if bfb.pixel(W - 1 - x, y):
                    out[base + (x >> 3)] |= 0x80 >> (x & 7)
        return out
    if mode == 3:
        out = bytearray(len(bb))
        for y in range(BAND_H):
            base = y * ROW_BYTES
            for x in range(W):
                if bfb.pixel(W - 1 - x, y):
                    out[base + (x >> 3)] |= 0x80 >> (x & 7)
        return bytearray(REV[b] for b in out)
    if mode == 4:
        return bytearray(b ^ 0xFF for b in bb)
    raise ValueError(mode)


main = bytearray(drv.BUFFER_SIZE)
for k in range(5):
    band = build_band(str(k), k)
    off = k * BAND_H * ROW_BYTES
    main[off:off + len(band)] = band

epd = drv.EPD()
epd.init()

t0 = time.ticks_ms()
epd.display(main)
print("display() took %d ms" % time.ticks_diff(time.ticks_ms(), t0))
print("bands top->bottom: 0=asis 1=bitrev 2=mirror 3=bitrev+mirror 4=inverted")
