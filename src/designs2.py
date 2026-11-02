# designs2.py — 17 candidate timer faces.
#
# Each is fn(cv, mm, ss, frame) and redraws the whole screen. They are meant
# to be visually unrelated to each other: pixel art, typography, retro
# hardware, print, geometry.

import math

import font5x7 as f7
import sprites
import gfx

BLACK = 0
WHITE = 1
BAYER = gfx.BAYER


def mmss(mm, ss):
    return "%02d:%02d" % (mm, ss)


def dither(cv, x, y, w, h, level):
    gfx.dither_rect(cv, x, y, w, h, level)


# ============================================================ 1. DINO
# Chrome offline runner: pixel dino, scrolling cacti, ground, sky digits.

def dino(cv, mm, ss, frame):
    cv.fill(WHITE)
    f7.draw_centred(cv, mmss(mm, ss), 6, 4, BLACK)

    gy = 100
    cv.hline(0, gy, cv.w, BLACK)
    for i in range(0, cv.w, 13):
        cv.hline(i, gy + 4, 6, BLACK)

    cx = (cv.w + 20 - (frame * 5) % (cv.w + 40))
    sprites.blit(cv, sprites.CLOUD, cx, 46)

    for k in range(2):
        x = (cv.w + 40 - (frame * 16 + k * 140) % (cv.w + 90))
        sprites.blit(cv, sprites.CACTUS, x, gy - 16)

    sp = sprites.DINO_A if (frame & 1) else sprites.DINO_B
    sprites.blit(cv, sp, 18, gy - 22)


# ============================================================ 2. INVADERS
# Space Invaders: three rows marching, digits below.

def invaders(cv, mm, ss, frame):
    cv.fill(WHITE)
    shift = (frame % 4) * 3
    for r in range(3):
        for c in range(6):
            sp = sprites.ALIEN_A if ((frame + r + c) & 1) else sprites.ALIEN_B
            sprites.blit(cv, sp, 12 + c * 38 + shift, 6 + r * 20, 2)
    f7.draw_centred(cv, mmss(mm, ss), 86, 3, BLACK)


# ============================================================ 3. FLIP
# Split-flap clock: black cards, white digits, hinge line.

def flip(cv, mm, ss, frame):
    cv.fill(WHITE)
    d = "%02d%02d" % (mm, ss)
    for i in range(4):
        x = 12 + i * 58
        cv.fill_rect(x, 22, 52, 76, BLACK)
        cv.hline(x, 60, 52, WHITE)
        cv.fill_rect(x + 2, 58, 4, 4, WHITE)
        cv.fill_rect(x + 46, 58, 4, 4, WHITE)
        f7.draw(cv, d[i], x + 16, 46, 4, WHITE)
    cv.fill_rect(124, 48, 4, 4, BLACK)
    cv.fill_rect(124, 64, 4, 4, BLACK)


# ============================================================ 4. SEVENSEG
# Mechanical 7-segment, thick bars, unlit segments ghosted in dither.

def sevenseg(cv, mm, ss, frame):
    cv.fill(WHITE)
    d = "%02d%02d" % (mm, ss)
    for i in range(4):
        gfx.seg7(cv, d[i], 10 + i * 58, 18, 44, 78, 7, BLACK, ghost=3)
    cv.fill_rect(116, 44, 6, 6, BLACK)
    cv.fill_rect(116, 64, 6, 6, BLACK)


# ============================================================ 5. LCD
# Calculator look: thin segments, faint ghosts, battery, label.

def lcd(cv, mm, ss, frame):
    cv.fill(WHITE)
    cv.rect(3, 3, cv.w - 6, cv.h - 6, BLACK)
    d = "%02d%02d" % (mm, ss)
    for i in range(4):
        gfx.seg7(cv, d[i], 14 + i * 48, 26, 40, 66, 3, BLACK, ghost=2)
    cv.fill_rect(104, 50, 5, 5, BLACK)
    cv.fill_rect(104, 66, 5, 5, BLACK)

    cv.rect(196, 8, 34, 13, BLACK)
    cv.fill_rect(230, 11, 3, 7, BLACK)
    cv.fill_rect(199, 11, 20, 7, BLACK)

    cv.text("TIMER", 10, 100, BLACK, 1)
    cv.text("SEC", 170, 100, BLACK, 1)


# ============================================================ 6. TERMINAL
# Inverted terminal: white on black, prompt, blinking block cursor.

def terminal(cv, mm, ss, frame):
    cv.fill(BLACK)
    cv.text("$ timer --start", 6, 8, WHITE, 1)
    f7.draw(cv, mmss(mm, ss), 8, 26, 5, WHITE)
    if frame & 1:
        cv.fill_rect(8 + f7.width(mmss(mm, ss), 5) + 8, 26, 22, 35, WHITE)
    cv.text("> elapsed", 6, 76, WHITE, 1)
    cv.text("  sensor ok", 6, 90, WHITE, 1)
    cv.text("  epd ok", 6, 104, WHITE, 1)


# ============================================================ 7. SWISS
# Helvetica-poster logic: one huge number, a rule, an accent block.

def swiss(cv, mm, ss, frame):
    cv.fill(WHITE)
    cv.text("ELAPSED", 4, 4, BLACK, 1)
    cv.hline(0, 16, cv.w, BLACK)
    f7.draw(cv, mmss(mm, ss), 8, 32, 6, BLACK)
    cv.hline(0, 88, cv.w, BLACK)
    cv.fill_rect(0, 96, 26, 10, BLACK)
    cv.text("MIN  SEC", 32, 97, BLACK, 1)


# ============================================================ 8. NEWSPAPER
# Masthead, double rules, big digits, small print.

def newspaper(cv, mm, ss, frame):
    cv.fill(WHITE)
    cv.text("THE TIMER", 6, 4, BLACK, 2)
    cv.hline(0, 21, cv.w, BLACK)
    cv.hline(0, 24, cv.w, BLACK)
    cv.text("VOL. I   NO. 250", 6, 28, BLACK, 1)
    cv.hline(0, 40, cv.w, BLACK)
    f7.draw_centred(cv, mmss(mm, ss), 46, 5, BLACK)
    cv.hline(0, 88, cv.w, BLACK)
    cv.text("ELAPSED SINCE TRIGGER", 6, 94, BLACK, 1)
    cv.text("PRICE 0.00", 6, 106, BLACK, 1)


# ============================================================ 9. CAT
# A sitting pixel cat, tail switching, digits above.

def cat(cv, mm, ss, frame):
    cv.fill(WHITE)
    f7.draw_centred(cv, mmss(mm, ss), 6, 3, BLACK)
    sp = sprites.CAT_A if (frame & 1) else sprites.CAT_B
    sprites.blit(cv, sp, 95, 46, 3)
    cv.hline(0, 108, cv.w, BLACK)


# ============================================================ 10. MOON
# Dithered moon, stars, a small astronaut. Digits top-left.

def moon(cv, mm, ss, frame):
    cv.fill(WHITE)
    for i in range(22):
        cv.pixel((i * 37 + 11) % cv.w, (i * 29 + 5) % 52, BLACK)

    cx, cy, r = 186, 64, 46
    for y in range(cy - r, cy + r):
        dy = y - cy
        for x in range(cx - r, cx + r):
            dx = x - cx
            d2 = dx * dx + dy * dy
            if d2 > r * r:
                continue
            z = math.sqrt(r * r - d2) / r
            lum = (-dx * 0.42 - dy * 0.38 + z * 0.82) / r * 46
            if lum > 0 and int(lum * 6) > BAYER[y & 3][x & 3]:
                cv.pixel(x, y, BLACK)

    sprites.blit(cv, sprites.ASTRONAUT, 34, 66, 3)
    f7.draw(cv, mmss(mm, ss), 8, 8, 3, BLACK)


# ============================================================ 11. SKYLINE
# City silhouette, lit windows, digits in the sky.

def skyline(cv, mm, ss, frame):
    cv.fill(WHITE)
    for i in range(16):
        cv.pixel((i * 53 + 17) % cv.w, (i * 31 + 3) % 40, BLACK)

    f7.draw_centred(cv, mmss(mm, ss), 6, 4, BLACK)

    heights = (34, 58, 42, 72, 38, 62, 46, 68, 40, 54, 48, 60)
    x = 2
    for i in range(len(heights)):
        h = heights[i]
        top = cv.h - h
        cv.fill_rect(x, top, 20, h, BLACK)
        for wy in range(top + 5, cv.h - 5, 9):
            for wx in range(x + 3, x + 17, 7):
                if (wx + wy + frame * 3) % 4:
                    cv.fill_rect(wx, wy, 3, 4, WHITE)
        x += 20


# ============================================================ 12. CASSETTE
# Tape shell, spinning reels, digits on the label.

def cassette(cv, mm, ss, frame):
    cv.fill(WHITE)
    cv.rect(6, 12, 238, 98, BLACK)
    cv.rect(10, 16, 230, 90, BLACK)

    cv.fill_rect(20, 22, 210, 40, BLACK)
    f7.draw_centred(cv, mmss(mm, ss), 28, 4, WHITE)

    cv.rect(24, 68, 202, 34, BLACK)
    for cx in (78, 172):
        cv.fill_circle(cx, 85, 15, BLACK)
        cv.fill_circle(cx, 85, 9, WHITE)
        for k in range(6):
            a = frame * 0.5 + k * math.pi / 3
            cv.line(cx, 85, cx + int(8 * math.cos(a)), 85 + int(8 * math.sin(a)), BLACK)


# ============================================================ 13. ECG
# Heart monitor: scrolling trace, digits, BPM.

def ecg(cv, mm, ss, frame):
    cv.fill(WHITE)
    f7.draw(cv, mmss(mm, ss), 8, 6, 4, BLACK)
    cv.text("BPM 60", 176, 12, BLACK, 1)

    base = 82
    cv.hline(0, base, cv.w, BLACK)
    for x in range(cv.w):
        ph = (x + frame * 12) % 72
        if ph < 10:
            v = 0
        elif ph < 14:
            v = 6
        elif ph < 18:
            v = 0
        elif ph < 20:
            v = -7
        elif ph < 23:
            v = 44
        elif ph < 26:
            v = -14
        elif ph < 36:
            v = 0
        elif ph < 46:
            v = 9
        else:
            v = 0
        if v:
            cv.vline(x, base - v, v if v > 0 else 1, BLACK)
            cv.pixel(x, base, BLACK)
        else:
            cv.pixel(x, base, BLACK)


# ============================================================ 14. DOTMATRIX
# LED dot-matrix digits on a dot grid.

def dotmatrix(cv, mm, ss, frame):
    cv.fill(WHITE)
    for y in range(2, cv.h, 5):
        for x in range(2, cv.w, 5):
            cv.pixel(x, y, BLACK)

    s = mmss(mm, ss)
    w = f7.width(s, 5)
    x = (cv.w - w) // 2
    cv.fill_rect(x - 6, 22, w + 12, 45, WHITE)
    f7.draw(cv, s, x, 26, 5, BLACK, dots=True)


# ============================================================ 15. BARCODE
# Industrial label: barcode, model number, serial.

def barcode(cv, mm, ss, frame):
    cv.fill(WHITE)
    cv.rect(3, 3, cv.w - 6, cv.h - 6, BLACK)
    cv.text("MODEL 250-122", 10, 9, BLACK, 1)

    pattern = (1, 0, 2, 0, 1, 1, 0, 2, 1, 0, 1, 2, 0, 1, 1, 0, 2, 0,
               1, 1, 2, 0, 1, 0, 2, 1, 0, 1, 1, 0, 2, 1, 0, 2, 1)
    x = 12
    for wdt in pattern:
        if wdt:
            cv.fill_rect(x, 22, wdt * 2, 36, BLACK)
        x += wdt * 2 + 3
        if x > 232:
            break

    f7.draw_centred(cv, mmss(mm, ss), 64, 4, BLACK)
    cv.text("SN 0000-0000", 10, 102, BLACK, 1)


# ============================================================ 16. MONDRIAN
# Rectangles, thick black rules, digits in the one calm white field.

def mondrian(cv, mm, ss, frame):
    cv.fill(WHITE)
    cv.fill_rect(0, 0, 60, 40, BLACK)
    cv.fill_rect(0, 86, 40, 36, BLACK)
    cv.fill_rect(210, 0, 40, 50, BLACK)
    cv.fill_rect(200, 96, 50, 26, BLACK)

    cv.fill_rect(62, 0, 4, cv.h, BLACK)
    cv.fill_rect(204, 0, 4, cv.h, BLACK)
    cv.fill_rect(0, 42, cv.w, 4, BLACK)
    cv.fill_rect(0, 82, cv.w, 4, BLACK)

    f7.draw(cv, mmss(mm, ss), 72, 54, 4, BLACK)


# ============================================================ 17. TAPE
# Ticker tape: black band, perforations, white print.

def tape(cv, mm, ss, frame):
    cv.fill(WHITE)
    cv.text("TICKER", 6, 10, BLACK, 1)
    cv.text("250x122", 196, 10, BLACK, 1)

    cv.fill_rect(0, 28, cv.w, 64, BLACK)
    for x in range(5, cv.w, 15):
        cv.fill_rect(x, 32, 6, 5, WHITE)
        cv.fill_rect(x, 83, 6, 5, WHITE)

    f7.draw_centred(cv, mmss(mm, ss), 44, 5, WHITE)

    cv.text("ELAPSED", 6, 104, BLACK, 1)


# ============================================================ registry

DESIGNS = (
    ("DINO", dino),
    ("INVADERS", invaders),
    ("FLIP", flip),
    ("SEVENSEG", sevenseg),
    ("LCD", lcd),
    ("TERMINAL", terminal),
    ("SWISS", swiss),
    ("NEWSPAPER", newspaper),
    ("CAT", cat),
    ("MOON", moon),
    ("SKYLINE", skyline),
    ("CASSETTE", cassette),
    ("ECG", ecg),
    ("DOTMATRIX", dotmatrix),
    ("BARCODE", barcode),
    ("MONDRIAN", mondrian),
    ("TAPE", tape),
)
