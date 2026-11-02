# cockpit.py — five STANDBY screens: a shuttle cockpit with the moon outside.
#
# Everything is white ink on black. "Shading" is Bayer dithering at different
# densities — level 0 is empty, 16 is solid — which is how you get greys out of
# one bit.
#
# Each design is fn(cv, frame) and draws the full panel. The status line
# (STBY-0000) is stamped on afterwards by render(), with a black patch behind
# it so it stays legible whatever the design does in that corner.

import math

import font5x7 as f7
import sprites

BLACK = 0
WHITE = 1

BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


# ---------------------------------------------------------------- helpers

def dither_fill(cv, x, y, w, h, level, c=WHITE):
    for yy in range(y, y + h):
        row = BAYER[yy & 3]
        for xx in range(x, x + w):
            if row[xx & 3] < level:
                cv.pixel(xx, yy, c)


def dither_grad(cv, x, y, w, h, l0, l1, c=WHITE):
    """Vertical dither gradient from level l0 at the top to l1 at the bottom."""
    span = h - 1 if h > 1 else 1
    for yy in range(h):
        lv = l0 + (l1 - l0) * yy // span
        row = BAYER[(y + yy) & 3]
        for xx in range(w):
            if row[(x + xx) & 3] < lv:
                cv.pixel(x + xx, y + yy, c)


def disc(cv, cx, cy, r, c=WHITE):
    for y in range(cy - r, cy + r + 1):
        dy = y - cy
        dx = int(math.sqrt(max(0, r * r - dy * dy)))
        cv.hline(cx - dx, y, 2 * dx + 1, c)


def ring(cv, cx, cy, r, t, c=WHITE):
    inner = (r - t) * (r - t)
    outer = (r + t) * (r + t)
    for y in range(cy - r - t, cy + r + t + 1):
        dy = y - cy
        for x in range(cx - r - t, cx + r + t + 1):
            dx = x - cx
            d2 = dx * dx + dy * dy
            if inner <= d2 <= outer:
                cv.pixel(x, y, c)


def moon(cv, cx, cy, r, c=WHITE, lx=-0.45, ly=-0.40, lz=0.80):
    """A lit sphere. Terminator falls out of the dot product with the light."""
    for y in range(cy - r, cy + r + 1):
        dy = y - cy
        row = BAYER[y & 3]
        for x in range(cx - r, cx + r + 1):
            dx = x - cx
            d2 = dx * dx + dy * dy
            if d2 > r * r:
                continue
            z = math.sqrt(r * r - d2) / r
            lum = (dx / r) * lx + (dy / r) * ly + z * lz
            if lum > 0 and int(lum * 7) > row[x & 3]:
                cv.pixel(x, y, c)


def stars(cv, n=46, seed=7, ymax=None):
    ymax = ymax if ymax is not None else cv.h
    for i in range(n):
        x = (i * 37 + seed * 13) % cv.w
        y = (i * 29 + seed * 7) % ymax
        cv.pixel(x, y, WHITE)


# ---------------------------------------------------------------- 1. PORTHOLE

def porthole(cv, frame):
    cv.fill(BLACK)
    cx, cy, r = 92, 58, 46

    # space seen through the glass
    stars(cv, 30, 3, cy + r)
    moon(cv, 106, 44, 26)

    # riveted rim
    ring(cv, cx, cy, r + 3, 2, WHITE)
    ring(cv, cx, cy, r + 8, 1, WHITE)
    for k in range(12):
        a = k * math.pi / 6
        rx = cx + int((r + 5) * math.cos(a))
        ry = cy + int((r + 5) * math.sin(a))
        cv.fill_rect(rx - 1, ry - 1, 3, 3, WHITE)

    # cabin wall around the porthole, shaded away from the glass
    for y in range(cv.h):
        dy = y - cy
        for x in range(cv.w):
            dx = x - cx
            d2 = dx * dx + dy * dy
            if d2 <= (r + 9) * (r + 9):
                continue
            dist = int(math.sqrt(d2)) - (r + 9)
            lv = 11 - dist // 6
            if lv > 0 and BAYER[y & 3][x & 3] < lv:
                cv.pixel(x, y, WHITE)


# ---------------------------------------------------------------- 2. PANORAMA

def panorama(cv, frame):
    cv.fill(BLACK)

    # windshield
    cv.rect(6, 4, 238, 78, WHITE)
    cv.rect(9, 7, 232, 72, WHITE)
    stars(cv, 40, 5, 76)
    moon(cv, 196, 34, 24)

    # glass reflection: two soft diagonal bands
    for i in range(26):
        x = 30 + i * 3
        dither_fill(cv, x, 10 + i, 2, 40 - i, 3)

    # centre strut
    cv.fill_rect(120, 4, 5, 78, WHITE)

    # dashboard
    dither_grad(cv, 0, 86, cv.w, 36, 12, 5)
    cv.hline(0, 86, cv.w, WHITE)

    # two control yokes
    for bx in (52, 190):
        cv.fill_rect(bx - 3, 92, 7, 22, WHITE)
        cv.fill_rect(bx - 12, 92, 25, 5, WHITE)

    # screens
    for sx in (96, 138):
        cv.rect(sx, 92, 30, 18, WHITE)
        dither_fill(cv, sx + 2, 94, 26, 14, 4)


# ---------------------------------------------------------------- 3. SEAT

def seat(cv, frame):
    cv.fill(BLACK)

    # window on the right
    cv.rect(126, 8, 118, 74, WHITE)
    cv.rect(130, 12, 110, 66, WHITE)
    stars(cv, 26, 9, 76)
    moon(cv, 200, 40, 22)

    # cabin wall, darker toward the left
    dither_grad(cv, 0, 0, 126, 122, 4, 12)

    # pilot seat: headrest, back, base
    disc(cv, 46, 34, 16, WHITE)
    dither_fill(cv, 30, 46, 32, 44, 12)
    cv.rect(30, 46, 32, 44, WHITE)
    dither_fill(cv, 24, 88, 52, 12, 8)
    cv.rect(24, 88, 52, 12, WHITE)

    # armrest with buttons
    cv.fill_rect(62, 62, 34, 6, WHITE)
    for k in range(4):
        disc(cv, 68 + k * 8, 65, 2, BLACK)
        ring(cv, 68 + k * 8, 65, 2, 1, WHITE)

    # floor shadow
    dither_fill(cv, 0, 104, 126, 18, 6)


# ---------------------------------------------------------------- 4. CONSOLE

def console(cv, frame):
    cv.fill(BLACK)

    # window strip along the top
    cv.rect(4, 4, 242, 34, WHITE)
    stars(cv, 34, 11, 36)
    moon(cv, 214, 20, 14)

    # angled console face
    dither_grad(cv, 0, 42, cv.w, 80, 5, 13)
    cv.hline(0, 42, cv.w, WHITE)

    # three round gauges
    for i in range(3):
        gx = 44 + i * 54
        disc(cv, gx, 74, 18, BLACK)
        ring(cv, gx, 74, 18, 2, WHITE)
        dither_fill(cv, gx - 15, 59, 30, 30, 2)
        # needle
        a = -2.2 + i * 0.9
        cv.line(gx, 74, gx + int(13 * math.cos(a)), 74 + int(13 * math.sin(a)), WHITE)
        disc(cv, gx, 74, 2, WHITE)

    # toggle switches
    for i in range(7):
        sx = 24 + i * 22
        cv.fill_rect(sx, 100, 3, 10, WHITE)
        cv.fill_rect(sx - 3, 96, 9, 4, WHITE)

    # a small readout screen
    cv.rect(176, 96, 66, 20, WHITE)
    dither_fill(cv, 179, 99, 60, 14, 5)


# ---------------------------------------------------------------- 5. GAUGE

def gauge(cv, frame):
    cv.fill(BLACK)

    # big primary gauge
    cx, cy, r = 74, 62, 46
    disc(cv, cx, cy, r + 8, BLACK)
    ring(cv, cx, cy, r + 8, 3, WHITE)
    dither_fill(cv, cx - r, cy - r, 2 * r, 2 * r, 2)
    ring(cv, cx, cy, r, 2, WHITE)

    # ticks
    for k in range(13):
        a = -math.pi * 1.15 + k * (math.pi * 1.3 / 12)
        x0 = cx + int((r - 8) * math.cos(a))
        y0 = cy + int((r - 8) * math.sin(a))
        x1 = cx + int((r - 2) * math.cos(a))
        y1 = cy + int((r - 2) * math.sin(a))
        cv.line(x0, y0, x1, y1, WHITE)

    # needle
    a = -2.1
    cv.line(cx, cy, cx + int((r - 10) * math.cos(a)), cy + int((r - 10) * math.sin(a)), WHITE)
    disc(cv, cx, cy, 4, WHITE)

    # secondary gauges
    for gx, gy, gr in ((168, 40, 20), (206, 76, 16)):
        disc(cv, gx, gy, gr + 4, BLACK)
        ring(cv, gx, gy, gr + 4, 2, WHITE)
        dither_fill(cv, gx - gr, gy - gr, 2 * gr, 2 * gr, 2)
        ring(cv, gx, gy, gr, 1, WHITE)
        cv.line(gx, gy, gx + int((gr - 4) * math.cos(0.7)),
                gy + int((gr - 4) * math.sin(0.7)), WHITE)

    # window sliver, top right
    cv.rect(150, 4, 96, 22, WHITE)
    stars(cv, 14, 13, 26)
    moon(cv, 224, 14, 8)

    # panel shadow
    dither_fill(cv, 0, 108, cv.w, 14, 4)


# ---------------------------------------------------------------- standby

ASTRO_X = 8
ASTRO_Y = 9
ASTRO_SCALE = 2


def standby(cv, label, count):
    """The CONSOLE cockpit, with the astronaut floating in the window."""
    console(cv, 0)
    sprites.blit(cv, sprites.ASTRONAUT, ASTRO_X, ASTRO_Y, ASTRO_SCALE, WHITE)
    render(cv, label, count)


# ---------------------------------------------------------------- registry

DESIGNS = (
    ("PORTHOLE", porthole),
    ("PANORAMA", panorama),
    ("SEAT", seat),
    ("CONSOLE", console),
    ("GAUGE", gauge),
)


def render(cv, label, count, frame=0):
    """Stamp the status line over an already-drawn design.

    Does NOT clear the panel — the design is drawn first by the caller.
    """
    s = "%s-%04d" % (label, count)
    w = cv.text_width(s, 1)
    x = cv.w - w - 3
    y = cv.h - 10
    cv.fill_rect(x - 2, y - 1, w + 4, 10, BLACK)
    cv.text(s, x, y, WHITE, 1)
