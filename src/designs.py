# designs.py — candidate faces for the timer. All digit-based, no ruler.
#
# Every design is a function (cv, mm, ss, frame) that redraws the whole screen.
#
#   big      minimal, one huge MM:SS
#   poster   bold double frame + caption bar
#   nixie    four tubes with a dithered glow, colon between the pairs
#   life     game of life crawling around a knocked-out digit panel
#   duck     a little duck hopping along the bottom

import math
import random

BLACK = 0
WHITE = 1

BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


# ------------------------------------------------------------------ helpers

def dither_rect(cv, x, y, w, h, level):
    """Fill a rect with a Bayer pattern; level 0 = empty, 16 = solid."""
    for yy in range(y, y + h):
        row = BAYER[yy & 3]
        for xx in range(x, x + w):
            if row[xx & 3] < level:
                cv.pixel(xx, yy, BLACK)


def mmss(mm, ss):
    return "%02d:%02d" % (mm, ss)


def centred(cv, s, y, scale, c=BLACK):
    cv.text(s, (cv.w - cv.text_width(s, scale)) // 2, y, c, scale)


# ------------------------------------------------------------------ 1. big

def big(cv, mm, ss, frame):
    cv.fill(WHITE)
    centred(cv, mmss(mm, ss), 38, 5)
    centred(cv, "ELAPSED", 98, 1)


# ------------------------------------------------------------------ 2. poster

def poster(cv, mm, ss, frame):
    cv.fill(WHITE)
    cv.rect(2, 2, cv.w - 4, cv.h - 4, BLACK)
    cv.rect(6, 6, cv.w - 12, cv.h - 12, BLACK)
    centred(cv, mmss(mm, ss), 26, 4)
    cv.fill_rect(6, cv.h - 24, cv.w - 12, 18, BLACK)
    centred(cv, "T I M E R", cv.h - 21, 1, WHITE)


# ------------------------------------------------------------------ 3. nixie

TUBE_W = 46
TUBE_H = 92
TUBE_Y = 12
TUBE_X = (21, 75, 129, 183)


def nixie(cv, mm, ss, frame):
    cv.fill(WHITE)
    digits = "%02d%02d" % (mm, ss)

    for i in range(4):
        x = TUBE_X[i]
        cv.rect(x, TUBE_Y, TUBE_W, TUBE_H, BLACK)
        # glow: two nested dithered bands, digit painted over the top
        dither_rect(cv, x + 4, TUBE_Y + 22, TUBE_W - 8, 46, 3)
        dither_rect(cv, x + 8, TUBE_Y + 28, TUBE_W - 16, 34, 6)
        d = digits[i]
        cv.text(d, x + (TUBE_W - 32) // 2, TUBE_Y + 30, BLACK, 4)

    # colon between the minute and second pairs
    cv.fill_rect(124, 50, 3, 3, BLACK)
    cv.fill_rect(124, 62, 3, 3, BLACK)

    # base plate
    cv.fill_rect(0, 106, cv.w, 16, BLACK)


# ------------------------------------------------------------------ 4. life

BOX_X, BOX_Y, BOX_W, BOX_H = 22, 30, 206, 62

_life = None


class LifeField:
    def __init__(self, cv, cell=4, density=0.22):
        self.cell = cell
        self.cols = cv.w // cell
        self.rows = cv.h // cell
        self.n = self.cols * self.rows
        self.grid = bytearray(self.n)
        random.seed(11)
        for y in range(self.rows):
            for x in range(self.cols):
                if self.blocked(x * cell, y * cell):
                    continue
                if random.random() < density:
                    self.grid[y * self.cols + x] = 1

    def blocked(self, px, py):
        return (BOX_X <= px < BOX_X + BOX_W) and (BOX_Y <= py < BOX_Y + BOX_H)

    def step(self):
        c = self.cols
        g = self.grid
        nxt = bytearray(self.n)
        for y in range(self.rows):
            ym = ((y - 1) % self.rows) * c
            y0 = y * c
            yp = ((y + 1) % self.rows) * c
            for x in range(c):
                xm = (x - 1) % c
                xp = (x + 1) % c
                alive = g[y0 + x]
                k = (g[ym + xm] + g[ym + x] + g[ym + xp]
                     + g[y0 + xm] + g[y0 + xp]
                     + g[yp + xm] + g[yp + x] + g[yp + xp])
                if k == 3 or (alive and k == 2):
                    if not self.blocked(x * self.cell, y * self.cell):
                        nxt[y0 + x] = 1
        self.grid = nxt


def life(cv, mm, ss, frame):
    global _life
    if _life is None:
        _life = LifeField(cv)

    cv.fill(WHITE)
    cell = _life.cell
    g = _life.grid
    c = _life.cols
    for y in range(_life.rows):
        base = y * c
        py = y * cell
        for x in range(c):
            if g[base + x]:
                cv.fill_rect(x * cell, py, cell, cell, BLACK)

    # knock the centre out and put the digits there
    cv.fill_rect(BOX_X, BOX_Y, BOX_W, BOX_H, WHITE)
    centred(cv, mmss(mm, ss), BOX_Y + 15, 4)

    _life.step()


# ------------------------------------------------------------------ 5. duck

def draw_duck(cv, x, y, frame):
    # tail
    cv.fill_triangle(x - 12, y - 3, x - 24, y - 12, x - 12, y + 5, BLACK)
    # body
    cv.fill_ellipse(x, y, 15, 10, BLACK)
    # neck + head
    cv.fill_ellipse(x + 11, y - 8, 6, 9, BLACK)
    cv.fill_circle(x + 12, y - 15, 8, BLACK)
    # beak
    cv.fill_triangle(x + 19, y - 18, x + 29, y - 15, x + 19, y - 12, BLACK)
    # eye
    cv.fill_circle(x + 14, y - 17, 2, WHITE)
    # wing
    cv.fill_ellipse(x - 3, y - 1, 8, 5, WHITE)
    # legs
    if frame & 1:
        cv.vline(x - 5, y + 9, 9, BLACK)
        cv.vline(x + 6, y + 9, 6, BLACK)
    else:
        cv.vline(x - 5, y + 9, 6, BLACK)
        cv.vline(x + 6, y + 9, 9, BLACK)


def duck(cv, mm, ss, frame):
    cv.fill(WHITE)
    centred(cv, mmss(mm, ss), 8, 3)

    cv.hline(0, 106, cv.w, BLACK)
    for i in range(0, cv.w, 16):
        cv.vline(i, 106, 3, BLACK)

    hop = int(abs(math.sin(frame * 0.55)) * 20)
    x = 34 + (frame * 9) % 180
    draw_duck(cv, x, 88 - hop, frame)


# ------------------------------------------------------------------ registry

DESIGNS = (
    ("BIG", big),
    ("POSTER", poster),
    ("NIXIE", nixie),
    ("LIFE", life),
    ("DUCK", duck),
)
