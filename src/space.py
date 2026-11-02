# space.py — a nicely shaded moon, drawn with ordered dithering.
#
# An 8x8 Bayer matrix gives 64 grey levels instead of the 16 you get from 4x4,
# which is the difference between a visible staircase and a smooth terminator.
# The sphere is shaded with a plain Lambert dot product; the dither turns the
# resulting float luminance into one bit.

import math
import random
import time

import sprites

random.seed(time.ticks_us())

BLACK = 0
WHITE = 1

BAYER8 = (
    (0, 32, 8, 40, 2, 34, 10, 42),
    (48, 16, 56, 24, 50, 18, 58, 26),
    (12, 44, 4, 36, 14, 46, 6, 38),
    (60, 28, 52, 20, 62, 30, 54, 22),
    (3, 35, 11, 43, 1, 33, 9, 41),
    (51, 19, 59, 27, 49, 17, 57, 25),
    (15, 47, 7, 39, 13, 45, 5, 37),
    (63, 31, 55, 23, 61, 29, 53, 21),
)


def sphere(cv, cx, cy, r, lx=-0.50, ly=-0.45, lz=0.74, c=WHITE):
    """A lit sphere. Light comes from (lx, ly, lz), normalised enough for this."""
    for y in range(cy - r, cy + r + 1):
        dy = y - cy
        dy2 = dy * dy
        if dy2 > r * r:
            continue
        row = BAYER8[y & 7]
        for x in range(cx - r, cx + r + 1):
            dx = x - cx
            d2 = dx * dx + dy2
            if d2 > r * r:
                continue
            z = math.sqrt(r * r - d2) / r
            lum = (dx / r) * lx + (dy / r) * ly + z * lz
            if lum <= 0.0:
                continue
            if int(lum * 64) > row[x & 7]:
                cv.pixel(x, y, c)


def crater(cv, cx, cy, r, density, c=BLACK):
    """Darken a dithered disc — reads as a crater on the lit side."""
    for y in range(cy - r, cy + r + 1):
        dy = y - cy
        dy2 = dy * dy
        if dy2 > r * r:
            continue
        row = BAYER8[y & 7]
        for x in range(cx - r, cx + r + 1):
            dx = x - cx
            if dx * dx + dy2 > r * r:
                continue
            if row[x & 7] < density:
                cv.pixel(x, y, c)


def halo(cv, cx, cy, r, width, level, c=WHITE):
    """A faint dithered glow just outside the limb."""
    outer = r + width
    for y in range(cy - outer, cy + outer + 1):
        dy = y - cy
        row = BAYER8[y & 7]
        for x in range(cx - outer, cx + outer + 1):
            dx = x - cx
            d2 = dx * dx + dy * dy
            if d2 <= r * r or d2 > outer * outer:
                continue
            d = math.sqrt(d2) - r
            lv = int(level * (width - d) / width)
            if row[x & 7] < lv:
                cv.pixel(x, y, c)


CRATERS = (
    (-18, -14, 9, 20),
    (6, -22, 6, 16),
    (22, 4, 11, 18),
    (-8, 16, 7, 14),
    (14, 26, 5, 12),
    (-26, 8, 5, 12),
)


def moon(cv, cx, cy, r, light=(-0.50, -0.45, 0.74), craters=True, glow=True):
    if glow:
        halo(cv, cx, cy, r, 7, 6)
    sphere(cv, cx, cy, r, light[0], light[1], light[2])
    if craters:
        for dx, dy, cr, dens in CRATERS:
            crater(cv, cx + dx, cy + dy, cr, dens)


# ---------------------------------------------------------------- variants

def moon_front(cv, frame=0):
    """Full face, light from the upper left."""
    cv.fill(BLACK)
    moon(cv, 125, 61, 56)


def moon_side(cv, frame=0):
    """Light from the right — a fat gibbous with a strong terminator."""
    cv.fill(BLACK)
    moon(cv, 125, 61, 56, light=(0.62, -0.30, 0.72))


def moon_high(cv, frame=0):
    """Light from almost straight above."""
    cv.fill(BLACK)
    moon(cv, 125, 61, 56, light=(-0.12, -0.86, 0.50))


def moon_plain(cv, frame=0):
    """No craters, no glow — just the shading."""
    cv.fill(BLACK)
    moon(cv, 125, 61, 56, craters=False, glow=False)


# ---------------------------------------------------------------- standby

ASTRO_SCALE = 1          # smallest the sprite goes: 9 x 14 px
MOON_CX, MOON_CY, MOON_R = 125, 61, 56

# fixed anchor: the tether always leaves from the same point on the left edge
TETHER_X, TETHER_Y = 0, 61


def status(cv, label, count):
    """STBY-0000, bottom right, same spot as in every other state."""
    s = "%s-%04d" % (label, count)
    w = cv.text_width(s, 1)
    x = cv.w - w - 3
    y = cv.h - 10
    cv.fill_rect(x - 2, y - 1, w + 4, 10, BLACK)
    cv.text(s, x, y, WHITE, 1)


def blit_scaled(cv, rows, x, y, num, den, c=WHITE):
    """Nearest-neighbour blit at a fractional scale, e.g. 3/2 for 1.5x.

    Integer scaling only offers 1x or 2x, and 2x is a big jump from 9x14.
    """
    sh = len(rows)
    sw = len(rows[0])
    dh = sh * num // den
    dw = sw * num // den
    for dy in range(dh):
        row = rows[dy * den // num]
        for dx in range(dw):
            if row[dx * den // num] == "#":
                cv.pixel(x + dx, y + dy, c)


def faint_tether(cv, x0, y0, x1, y1, c=WHITE):
    """A 1 px dashed line — the thinnest, least assertive mark we can make."""
    steps = max(abs(x1 - x0), abs(y1 - y0))
    if steps < 1:
        return
    for i in range(steps + 1):
        if i & 1:
            continue
        f = i / float(steps)
        x = int(x0 + (x1 - x0) * f)
        y = int(y0 + (y1 - y0) * f + 3.0 * math.sin(f * 7.0))
        cv.pixel(x, y, c)


def standby(cv, label="STBY", count=0):
    """Plain shaded moon, astronaut on a faint tether to its left.

    The astronaut's height along the left limb is re-rolled every time this is
    called, so re-entering standby puts him somewhere new.
    """
    cv.fill(BLACK)
    moon(cv, MOON_CX, MOON_CY, MOON_R, craters=False, glow=False)

    ay = random.randint(12, 98)
    dy = ay + 10 - MOON_CY
    if abs(dy) < MOON_R:
        edge = MOON_CX - int(math.sqrt(MOON_R * MOON_R - dy * dy))
    else:
        edge = MOON_CX
    # gap from the limb is random too, so he is not always hugging the sphere
    gap = random.randint(14, 58)
    ax = edge - gap
    if ax < 2:
        ax = 2

    faint_tether(cv, TETHER_X, TETHER_Y, ax, ay + 10)
    blit_scaled(cv, sprites.ASTRONAUT, ax, ay, 3, 2, WHITE)
    status(cv, label, count)


VARIANTS = (
    ("FRONT", moon_front),
    ("SIDE", moon_side),
    ("HIGH", moon_high),
    ("PLAIN", moon_plain),
)
