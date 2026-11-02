# designs3.py — 10 more faces, all in the dot-matrix / LED family.
#
# Everything here is built from discrete dots on a grid, inverted (white dots
# on black) the way a real LED panel looks.

import math

import font5x7 as f7

BLACK = 0
WHITE = 1


def mmss(mm, ss):
    return "%02d:%02d" % (mm, ss)


def prand(i, f):
    """Cheap deterministic hash so animations look random but replay."""
    x = (i * 1103515245 + f * 12345 + 7) & 0x7FFFFFFF
    x ^= x >> 13
    return (x * 1103515245) & 0x7FFFFFFF


def led_text(cv, s, x, y, pitch=4, dsize=2, cell=1, c=WHITE):
    """Draw s as dots. Each font pixel becomes a cell x cell block of dots."""
    for i in range(len(s)):
        g = f7.GLYPHS.get(s[i])
        if g is None:
            continue
        for ry in range(7):
            row = g[ry]
            for rx in range(5):
                if row[rx] == "#":
                    for cy in range(cell):
                        for cx in range(cell):
                            cv.fill_rect(x + (i * 6 + rx * cell + cx) * pitch,
                                         y + (ry * cell + cy) * pitch,
                                         dsize, dsize, c)


def led_width(s, pitch=4, cell=1):
    return len(s) * 6 * cell * pitch


# ============================================================ 18. LEDBIG

def ledbig(cv, mm, ss, frame):
    cv.fill(BLACK)
    s = mmss(mm, ss)
    w = led_width(s, 4, 2)
    led_text(cv, s, (cv.w - w) // 2, 33, 4, 2, 2)


# ============================================================ 19. LEDSCROLL

def ledscroll(cv, mm, ss, frame):
    cv.fill(BLACK)
    msg = "  ELAPSED  " + mmss(mm, ss) + "  SENSOR  "
    w = led_width(msg, 4, 1)
    off = (frame * 14) % (w + cv.w)
    led_text(cv, msg, cv.w - off, 46, 4, 2, 1)
    led_text(cv, msg, cv.w - off + w + cv.w, 46, 4, 2, 1)


# ============================================================ 20. LEDWAVE

def ledwave(cv, mm, ss, frame):
    cv.fill(BLACK)
    for y in range(2, cv.h, 6):
        for x in range(2, cv.w, 6):
            v = (math.sin((x + frame * 7) * 0.055)
                 * math.cos((y - frame * 4) * 0.075))
            if v > 0.15:
                cv.fill_rect(x, y, 2, 2, WHITE)

    s = mmss(mm, ss)
    w = led_width(s, 4, 1)
    x0 = (cv.w - w) // 2
    cv.fill_rect(x0 - 6, 40, w + 12, 34, BLACK)
    led_text(cv, s, x0, 44, 4, 2, 1)


# ============================================================ 21. LEDHEART

HEART = (
    ".##...##.",
    "#########",
    "#########",
    "#########",
    ".#######.",
    "..#####..",
    "...###...",
    "....#....",
)


def ledheart(cv, mm, ss, frame):
    cv.fill(BLACK)
    beat = 1 if (frame % 5) < 2 else 0
    pitch = 6 + beat
    dsize = 3 + beat

    hx = 22
    hy = 34
    for ry in range(len(HEART)):
        row = HEART[ry]
        for rx in range(len(row)):
            if row[rx] == "#":
                cv.fill_rect(hx + rx * pitch, hy + ry * pitch, dsize, dsize, WHITE)

    s = mmss(mm, ss)
    led_text(cv, s, 100, 46, 4, 2, 1)


# ============================================================ 22. LEDLIFE

_life = None
_LCELL = 6


class DotLife:
    def __init__(self, cv):
        self.cols = cv.w // _LCELL
        self.rows = cv.h // _LCELL
        self.n = self.cols * self.rows
        self.grid = bytearray(self.n)
        for i in range(self.n):
            if prand(i, 3) % 100 < 20:
                self.grid[i] = 1

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
                a = g[y0 + x]
                k = (g[ym + xm] + g[ym + x] + g[ym + xp]
                     + g[y0 + xm] + g[y0 + xp]
                     + g[yp + xm] + g[yp + x] + g[yp + xp])
                if k == 3 or (a and k == 2):
                    nxt[y0 + x] = 1
        self.grid = nxt


def ledlife(cv, mm, ss, frame):
    global _life
    if _life is None:
        _life = DotLife(cv)

    cv.fill(BLACK)
    c = _life.cols
    g = _life.grid
    for y in range(_life.rows):
        base = y * c
        py = y * _LCELL
        for x in range(c):
            if g[base + x]:
                cv.fill_rect(x * _LCELL, py, 2, 2, WHITE)

    s = mmss(mm, ss)
    w = led_width(s, 4, 1)
    x0 = (cv.w - w) // 2
    cv.fill_rect(x0 - 8, 44, w + 16, 32, BLACK)
    cv.rect(x0 - 8, 44, w + 16, 32, WHITE)
    led_text(cv, s, x0, 48, 4, 2, 1)

    _life.step()


# ============================================================ 23. LEDRAIN

def ledrain(cv, mm, ss, frame):
    cv.fill(BLACK)
    col = 0
    while col < cv.w:
        head = (prand(col, frame) % (cv.h + 60)) - 30
        trail = 3 + prand(col, frame + 1) % 6
        for k in range(trail):
            y = head - k * 7
            if 0 <= y < cv.h:
                cv.fill_rect(col, y, 2, 2, WHITE)
        col += 8

    s = mmss(mm, ss)
    w = led_width(s, 4, 1)
    x0 = (cv.w - w) // 2
    cv.fill_rect(x0 - 8, 44, w + 16, 32, BLACK)
    led_text(cv, s, x0, 48, 4, 2, 1)


# ============================================================ 24. LEDEQ

def ledeq(cv, mm, ss, frame):
    cv.fill(BLACK)
    bars = 20
    for i in range(bars):
        h = 2 + int(7 * abs(math.sin(i * 0.55 + frame * 0.7)))
        for k in range(h):
            cv.fill_rect(5 + i * 12, cv.h - 10 - k * 7, 5, 4, WHITE)

    led_text(cv, mmss(mm, ss), 5, 8, 4, 2, 1)


# ============================================================ 25. LEDSPIRAL

def ledspiral(cv, mm, ss, frame):
    cv.fill(BLACK)
    cx, cy = 61, 61
    a = 0.0
    spin = frame * 0.18
    while a < 9 * math.pi:
        r = a * 2.0
        if r > 56:
            break
        x = cx + int(r * math.cos(a + spin))
        y = cy + int(r * math.sin(a + spin))
        cv.fill_rect(x, y, 2, 2, WHITE)
        a += 0.10

    led_text(cv, mmss(mm, ss), 126, 46, 4, 2, 1)


# ============================================================ 26. LEDFIRE

def ledfire(cv, mm, ss, frame):
    cv.fill(BLACK)
    for i in range(150):
        x = prand(i, frame) % cv.w
        y = cv.h - 4 - (prand(i, frame + 5) % 46)
        cv.fill_rect(x, y, 2, 2, WHITE)

    s = mmss(mm, ss)
    w = led_width(s, 4, 1)
    x0 = (cv.w - w) // 2
    cv.fill_rect(x0 - 8, 30, w + 16, 32, BLACK)
    led_text(cv, s, x0, 34, 4, 2, 1)


# ============================================================ 27. LEDCLOCK

def ledclock(cv, mm, ss, frame):
    cv.fill(BLACK)
    cx, cy, r = 61, 61, 52

    for i in range(60):
        a = -math.pi / 2 + i * 2 * math.pi / 60
        x = cx + int(r * math.cos(a))
        y = cy + int(r * math.sin(a))
        s = 3 if (i % 5 == 0) else 2
        cv.fill_rect(x, y, s, s, WHITE)

    am = -math.pi / 2 + (mm % 60) * 2 * math.pi / 60
    asec = -math.pi / 2 + ss * 2 * math.pi / 60
    cv.line(cx, cy, cx + int(28 * math.cos(am)), cy + int(28 * math.sin(am)), WHITE)
    cv.line(cx, cy, cx + int(44 * math.cos(asec)), cy + int(44 * math.sin(asec)), WHITE)
    cv.fill_rect(cx - 2, cy - 2, 4, 4, WHITE)

    led_text(cv, mmss(mm, ss), 126, 46, 4, 2, 1)


# ============================================================ registry

DESIGNS = (
    ("LEDBIG", ledbig),
    ("LEDSCROLL", ledscroll),
    ("LEDWAVE", ledwave),
    ("LEDHEART", ledheart),
    ("LEDLIFE", ledlife),
    ("LEDRAIN", ledrain),
    ("LEDEQ", ledeq),
    ("LEDSPIRAL", ledspiral),
    ("LEDFIRE", ledfire),
    ("LEDCLOCK", ledclock),
)
