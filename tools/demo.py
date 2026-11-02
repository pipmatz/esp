# demo.py — what this panel can do.
#
# Five scenes at ~1.6 fps (partial refresh measured at 615 ms).
# Run with:  mpremote run tools/demo.py
#
#   1. ruler        - the actual timer UI counting 0..30
#   2. game of life - Conway's, 4 px cells, wrapping edges
#   3. sphere       - a dithered sphere: 1-bit "greyscale" via Bayer 4x4
#   4. boot log     - text typed out character by character
#   5. marquee      - scaled text scrolling across
#
# E-paper can't do smooth motion. What it does beautifully is slow, deliberate
# change — and ordered dithering, which is how you get shading out of one bit.

import sys
import time
import math
import random

sys.path.append("/drivers")
sys.path.append("/src")

import config
import display
import ui

W = config.VIEW_W
H = config.VIEW_H
BLACK = 0
WHITE = 1

d = display.Display()
cv = d.cv
_times = []


def show(first=False):
    t0 = time.ticks_ms()
    if first:
        d.base()
    else:
        d.partial()
    _times.append(time.ticks_diff(time.ticks_ms(), t0))


# ------------------------------------------------------------------ 1. ruler

def scene_ruler():
    u = ui.UI(cv)
    u.draw_static()
    u.draw_counter(0)
    u.draw_state("RUN")
    show(first=True)
    for s in range(1, 31):
        u.draw_counter(s)
        u.draw_ruler(s)
        show()
    u.draw_state("STOP")
    show()


# ------------------------------------------------------------------ 2. life

def scene_life(generations=34):
    CW = 4
    cols = W // CW
    rows = H // CW
    n = cols * rows

    random.seed(7)
    grid = [1 if random.random() < 0.34 else 0 for _ in range(n)]

    for g in range(generations):
        cv.fill(WHITE)
        for y in range(rows):
            base = y * cols
            for x in range(cols):
                if grid[base + x]:
                    cv.fill_rect(x * CW, y * CW, CW, CW, BLACK)
        show(first=(g == 0))

        nxt = [0] * n
        for y in range(rows):
            ym = ((y - 1) % rows) * cols
            y0 = y * cols
            yp = ((y + 1) % rows) * cols
            for x in range(cols):
                xm = (x - 1) % cols
                xp = (x + 1) % cols
                c = grid[y0 + x]
                k = (grid[ym + xm] + grid[ym + x] + grid[ym + xp]
                     + grid[y0 + xm] + grid[y0 + xp]
                     + grid[yp + xm] + grid[yp + x] + grid[yp + xp])
                nxt[y0 + x] = 1 if (k == 3 or (c and k == 2)) else 0
        grid = nxt


# ------------------------------------------------------------------ 3. sphere

BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def scene_sphere():
    cx, cy, r = W // 2, H // 2, 56
    lx, ly, lz = -0.55, -0.62, 0.56
    inv = 1.0 / r

    cv.fill(WHITE)
    for y in range(H):
        dy = y - cy
        for x in range(W):
            dx = x - cx
            d2 = dx * dx + dy * dy
            if d2 > r * r:
                continue
            z = math.sqrt(r * r - d2) * inv
            lum = (dx * inv) * lx + (dy * inv) * ly + z * lz
            if lum <= 0.0:
                continue
            if int(lum * 255) > BAYER[y & 3][x & 3] * 16 + 8:
                cv.pixel(x, y, BLACK)
    show(first=True)


# ------------------------------------------------------------------ 4. boot

BOOT = (
    "> boot",
    "MicroPython v1.29.0",
    "ESP32-S3  N16R8",
    "flash 16MB  OK",
    "psram  8MB  OK",
    "epd 250x122 OK",
    "sensor GPIO10",
    "ready.",
)


def scene_boot():
    cv.fill(WHITE)
    show(first=True)

    y = 6
    for line in BOOT:
        # type two characters per frame
        for i in range(2, len(line) + 1, 2):
            cv.fill_rect(0, y, W, 8, WHITE)
            cv.text(line[:i], 4, y, BLACK, 1)
            cv.fill_rect(4 + i * 8, y, 6, 8, BLACK)   # cursor
            show()
        cv.fill_rect(0, y, W, 8, WHITE)
        cv.text(line, 4, y, BLACK, 1)
        show()
        y += 12


# ------------------------------------------------------------------ 5. marquee

def scene_marquee(frames=30):
    msg = "MICROPYTHON  *  E-PAPER  *  250x122  *  "
    tw = cv.text_width(msg, 2)
    for i in range(frames):
        cv.fill(WHITE)
        off = (i * 10) % (tw + W)
        cv.text(msg, W - off, 30, BLACK, 2)
        cv.text(msg, W - off - tw - W, 30, BLACK, 2)
        cv.hline(0, 24, W, BLACK)
        cv.hline(0, 50, W, BLACK)
        show(first=(i == 0))


# ------------------------------------------------------------------ run

d.init()
t_start = time.ticks_ms()

print("1/5 ruler")
scene_ruler()
print("2/5 life")
scene_life()
print("3/5 sphere")
scene_sphere()
print("4/5 boot")
scene_boot()
print("5/5 marquee")
scene_marquee()

total = time.ticks_diff(time.ticks_ms(), t_start)
print("frames: %d" % len(_times))
print("avg frame: %d ms" % (sum(_times) // len(_times)))
print("total: %.1f s" % (total / 1000))
