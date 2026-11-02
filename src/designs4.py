# designs4.py — 15 iterations of the five chosen directions.
#
#   SPIRAL1..3    rotating / progressive / comet-trail spiral
#   TERM1..3      terminal, with persisted session count and wall-clock time
#   ASTRO1..3     astronaut on the moon, floating, walking
#   ROCKET1..3    rocket to the moon: cruise, boost, descent
#   PAC1..3       pac-man, white on black
#
# The terminal faces read the session counter from /sessions.txt and the clock
# from the RTC (see tools/settime.sh).

import math
import time

import font5x7 as f7
import sprites
import gfx
import sessions

BLACK = 0
WHITE = 1
BAYER = gfx.BAYER


def mmss(mm, ss):
    return "%02d:%02d" % (mm, ss)


def led_text(cv, s, x, y, pitch=4, dsize=2, cell=1, c=WHITE):
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


def now_hms():
    t = time.localtime()
    return "%02d:%02d:%02d" % (t[3], t[4], t[5])


def now_hm():
    t = time.localtime()
    return "%02d:%02d" % (t[3], t[4])


def today():
    t = time.localtime()
    return "%04d-%02d-%02d" % (t[0], t[1], t[2])


def moon_disc(cv, cx, cy, r, c=BLACK, light=(-0.42, -0.38, 0.82)):
    """A shaded sphere via Bayer dithering — reads as a lit moon."""
    lx, ly, lz = light
    for y in range(cy - r, cy + r):
        dy = y - cy
        row = BAYER[y & 3]
        for x in range(cx - r, cx + r):
            dx = x - cx
            d2 = dx * dx + dy * dy
            if d2 > r * r:
                continue
            z = math.sqrt(r * r - d2) / r
            lum = (dx / r) * lx + (dy / r) * ly + z * lz
            if lum > 0 and int(lum * 6) > row[x & 3]:
                cv.pixel(x, y, c)


def pacman(cv, x, y, r, mouth, c=WHITE, bg=BLACK):
    cv.fill_circle(x, y, r, c)
    if mouth > 0.03:
        cv.fill_triangle(
            x, y,
            x + int(r * math.cos(-mouth)), y + int(r * math.sin(-mouth)),
            x + int(r * math.cos(mouth)), y + int(r * math.sin(mouth)),
            bg)


# ============================================================ SPIRAL

def spiral1(cv, mm, ss, frame):
    cv.fill(BLACK)
    cx, cy = 61, 61
    spin = frame * 0.18
    a = 0.0
    while a < 9 * math.pi:
        r = a * 2.0
        if r > 56:
            break
        cv.fill_rect(cx + int(r * math.cos(a + spin)),
                     cy + int(r * math.sin(a + spin)), 2, 2, WHITE)
        a += 0.10
    led_text(cv, mmss(mm, ss), 126, 46, 4, 2, 1)


def spiral2(cv, mm, ss, frame):
    """The spiral *is* the progress bar: one dot per second, centre outward."""
    cv.fill(BLACK)
    cx, cy = 61, 61
    n = 60
    for i in range(n):
        a = i * (9 * math.pi / n)
        r = a * 2.0
        x = cx + int(r * math.cos(a))
        y = cy + int(r * math.sin(a))
        if i < ss:
            cv.fill_rect(x - 1, y - 1, 3, 3, WHITE)
        else:
            cv.pixel(x, y, WHITE)
    led_text(cv, mmss(mm, ss), 126, 46, 4, 2, 1)


def spiral3(cv, mm, ss, frame):
    cv.fill(BLACK)
    cx, cy = 61, 61
    n = 80
    head = (frame * 5) % n
    for i in range(n):
        a = i * (9 * math.pi / n)
        r = a * 2.0
        x = cx + int(r * math.cos(a))
        y = cy + int(r * math.sin(a))
        d = (head - i) % n
        if d < 8:
            cv.fill_rect(x - 1, y - 1, 3, 3, WHITE)
        elif d < 45:
            cv.pixel(x, y, WHITE)
    led_text(cv, mmss(mm, ss), 126, 46, 4, 2, 1)


# ============================================================ TERMINAL

def term1(cv, mm, ss, frame):
    cv.fill(BLACK)
    cv.text("$ timer --start", 6, 6, WHITE, 1)
    f7.draw(cv, mmss(mm, ss), 8, 20, 5, WHITE)
    if frame & 1:
        cv.fill_rect(8 + f7.width(mmss(mm, ss), 5) + 8, 20, 20, 34, WHITE)
    cv.text("session  #%d" % sessions.load(), 6, 66, WHITE, 1)
    cv.text("now      %s" % now_hms(), 6, 80, WHITE, 1)
    cv.text("> sensor armed", 6, 96, WHITE, 1)


def term2(cv, mm, ss, frame):
    cv.fill(BLACK)
    cv.rect(2, 2, cv.w - 4, cv.h - 4, WHITE)
    cv.hline(2, 16, cv.w - 4, WHITE)
    cv.text("TIMER MONITOR", 6, 5, WHITE, 1)

    cv.text("SESSIONS", 8, 22, WHITE, 1)
    f7.draw(cv, "%02d" % (sessions.load() % 100), 8, 34, 4, WHITE)

    cv.vline(84, 20, 58, WHITE)
    cv.text("ELAPSED", 92, 22, WHITE, 1)
    f7.draw(cv, mmss(mm, ss), 92, 34, 4, WHITE)

    cv.vline(196, 20, 58, WHITE)
    cv.text("NOW", 204, 22, WHITE, 1)
    cv.text(now_hm(), 204, 34, WHITE, 1)
    cv.text(today(), 204, 46, WHITE, 1)

    cv.hline(2, 90, cv.w - 4, WHITE)
    cv.text("uptime %s" % now_hms(), 6, 96, WHITE, 1)


def term3(cv, mm, ss, frame):
    cv.fill(BLACK)
    lines = (
        "boot ok",
        "sensor armed",
        "epd ready",
        "session %d" % sessions.load(),
        "elapsed %s" % mmss(mm, ss),
    )
    n = len(lines)
    y = 6
    for k in range(4):
        cv.text("[%s] %s" % (now_hms(), lines[(frame + k) % n]), 4, y, WHITE, 1)
        y += 11
    f7.draw_centred(cv, mmss(mm, ss), 62, 4, WHITE)


# ============================================================ ASTRONAUT

def astro1(cv, mm, ss, frame):
    cv.fill(WHITE)
    for i in range(20):
        cv.pixel((i * 37 + 11) % cv.w, (i * 29 + 5) % 44, BLACK)
    moon_disc(cv, 176, 78, 50, BLACK)
    sprites.blit(cv, sprites.ASTRONAUT, 44, 74, 3, BLACK)
    cv.hline(0, 116, cv.w, BLACK)
    f7.draw(cv, mmss(mm, ss), 8, 8, 3, BLACK)


def astro2(cv, mm, ss, frame):
    cv.fill(BLACK)
    for i in range(46):
        cv.pixel((i * 37 + 11) % cv.w, (i * 29 + 5) % cv.h, WHITE)

    ax = 152
    ay = 46 + int(12 * math.sin(frame * 0.5))
    for t in range(0, 25):
        f = t / 24.0
        x = int(10 + (ax - 10) * f)
        y = int(8 + (ay - 8) * f + 9 * math.sin(f * 6 + frame))
        cv.pixel(x, y, WHITE)

    sprites.blit(cv, sprites.ASTRONAUT, ax, ay, 3, WHITE)
    led_text(cv, mmss(mm, ss), 10, 88, 4, 2, 1)


def astro3(cv, mm, ss, frame):
    cv.fill(BLACK)
    # dithered lunar surface
    gfx.dither_rect(cv, 0, 92, cv.w, 30, 7)
    cv.hline(0, 92, cv.w, WHITE)

    # footprints behind the walker
    for i in range(7):
        fx = 16 + i * 20
        cv.fill_rect(fx, 104, 6, 3, BLACK)
        cv.fill_rect(fx + 8, 110, 6, 3, BLACK)

    ax = 70 + int(36 * math.sin(frame * 0.35))
    sprites.blit(cv, sprites.ASTRONAUT, ax, 50, 3, WHITE)
    led_text(cv, mmss(mm, ss), 8, 8, 4, 2, 1)


# ============================================================ ROCKET

def rocket1(cv, mm, ss, frame):
    cv.fill(BLACK)
    for i in range(30):
        cv.pixel((i * 41 + 7) % cv.w, (i * 23 + 11) % cv.h, WHITE)
    moon_disc(cv, 202, 38, 34, WHITE)

    rx = 40 + (frame * 7) % 110
    ry = 96 - (frame * 5) % 60
    sprites.blit(cv, sprites.ROCKET, rx, ry, 2, WHITE)
    cv.fill_triangle(rx + 6, ry + 34, rx + 16, ry + 34, rx + 11, ry + 48, WHITE)
    led_text(cv, mmss(mm, ss), 8, 100, 4, 2, 1)


def rocket2(cv, mm, ss, frame):
    cv.fill(BLACK)
    for i in range(26):
        y = (i * 17) % cv.h
        x = (i * 53 + frame * 22) % cv.w
        cv.hline(x, y, 9, WHITE)

    rx, ry = 108, 22
    sprites.blit(cv, sprites.ROCKET, rx, ry, 3, WHITE)
    for k in range(5):
        w = 14 - k * 2
        cv.fill_rect(rx + 16 - w // 2, ry + 51 + k * 6, w, 5, WHITE)
    led_text(cv, mmss(mm, ss), 8, 100, 4, 2, 1)


def rocket3(cv, mm, ss, frame):
    cv.fill(BLACK)
    for i in range(24):
        cv.pixel((i * 43 + 5) % 130, (i * 19 + 7) % cv.h, WHITE)

    moon_disc(cv, 196, 66, 58, WHITE)
    cv.fill_rect(150, 116, 90, 4, WHITE)

    ry = 16 + (frame * 5) % 46
    rx = 182
    sprites.blit(cv, sprites.ROCKET, rx, ry, 2, WHITE)
    for k in range(3):
        w = 10 - k * 2
        cv.fill_rect(rx + 6 - w // 2 + 5, ry + 34 + k * 5, w, 4, WHITE)
    led_text(cv, mmss(mm, ss), 8, 44, 4, 2, 1)


# ============================================================ PAC-MAN

def pac1(cv, mm, ss, frame):
    cv.fill(BLACK)
    led_text(cv, mmss(mm, ss), 5, 6, 4, 2, 1)

    gy = 84
    px = 24 + (frame * 16) % (cv.w - 64)
    for x in range(10, cv.w, 16):
        if x > px + 12:
            cv.fill_rect(x, gy - 1, 3, 3, WHITE)

    sprites.blit(cv, sprites.GHOST, px - 36, gy - 12, 2, WHITE)
    pacman(cv, px, gy, 10, 0.15 + 0.55 * abs(math.sin(frame * 0.9)), WHITE, BLACK)


def pac2(cv, mm, ss, frame):
    cv.fill(BLACK)
    led_text(cv, mmss(mm, ss), 5, 4, 4, 2, 1)

    cv.fill_rect(0, 44, cv.w, 3, WHITE)
    cv.fill_rect(0, 88, cv.w, 3, WHITE)
    for x in range(18, cv.w, 62):
        cv.fill_rect(x, 47, 3, 18, WHITE)
        cv.fill_rect(x + 31, 70, 3, 18, WHITE)

    px = 12 + (frame * 14) % (cv.w - 34)
    for x in range(10, cv.w, 14):
        if x > px + 10:
            cv.fill_rect(x, 64, 3, 3, WHITE)

    pacman(cv, px, 65, 9, 0.2 + 0.5 * abs(math.sin(frame * 0.9)), WHITE, BLACK)


def pac3(cv, mm, ss, frame):
    cv.fill(BLACK)
    pacman(cv, 56, 61, 46, 0.2 + 0.6 * abs(math.sin(frame * 0.7)), WHITE, BLACK)

    for i in range(4):
        x = 124 + i * 30
        cv.fill_rect(x, 56, 7, 7, WHITE)

    led_text(cv, mmss(mm, ss), 122, 14, 4, 2, 1)


# ============================================================ registry

DESIGNS = (
    ("SPIRAL1", spiral1),
    ("SPIRAL2", spiral2),
    ("SPIRAL3", spiral3),
    ("TERM1", term1),
    ("TERM2", term2),
    ("TERM3", term3),
    ("ASTRO1", astro1),
    ("ASTRO2", astro2),
    ("ASTRO3", astro3),
    ("ROCKET1", rocket1),
    ("ROCKET2", rocket2),
    ("ROCKET3", rocket3),
    ("PAC1", pac1),
    ("PAC2", pac2),
    ("PAC3", pac3),
)
