# astro.py — cartoony astronaut drifting on a tether, in white-on-black.
#
#   * stars are always visible, but change size so the field shimmers
#   * astronaut drifts on both axes, tether follows his backpack
#   * tether is a 2 px wavy line, no anchor block
#   * clock bottom-left:  MM:  small on top,  SS  huge below
#   * small status line bottom-right:  STATE-0000
#
# Animation only runs while the timer is running. In every other state the
# scene is drawn at frame 0 and stays put — no refresh, no ghosting.

import math
import random
import time

import font5x7 as f7
import digitfonts
import sprites

random.seed(time.ticks_us())

BLACK = 0
WHITE = 1

SCALE = 4
AX = 168          # astronaut sprite origin, drift is added on top
AY = 28

TETHER_X0, TETHER_Y0 = 6, 3

MIN_SCALE = 3     # the MM: row
SEC_SCALE = 8     # the SS row
CLOCK_X = 8
MIN_Y = 8
SEC_Y = 40

CLOCK_FONT = digitfonts.LCD

STATUS_SCALE = 1  # the bottom-right status line


STARS = (
    (16, 20), (44, 40), (78, 14), (112, 32), (208, 14), (234, 42),
    (28, 66), (96, 80), (140, 106), (226, 98), (60, 110), (190, 114),
    (128, 8), (52, 88),
)


def draw_stars(cv, frame, c=BLACK):
    """Every star is always drawn; only its size changes, so nothing blinks out.

    Each star gets its own pair of frequencies, so some twinkle lazily and a
    few chatter much faster than the rest.
    """
    for i in range(len(STARS)):
        x, y = STARS[i]
        f1 = 0.4 + (i * 7 % 5) * 0.45
        f2 = 1.0 + (i * 11 % 6) * 0.55
        v = (math.sin(frame * f1 + i * 2.1)
             + math.sin(frame * f2 + i * 0.9))
        if v > 1.5:
            cv.fill_rect(x - 2, y, 5, 1, c)
            cv.fill_rect(x, y - 2, 1, 5, c)
        elif v > 1.0:
            cv.fill_rect(x - 1, y, 3, 1, c)
            cv.fill_rect(x, y - 1, 1, 3, c)
        elif v > 0.2:
            cv.fill_rect(x, y, 2, 2, c)
        else:
            cv.pixel(x, y, c)


_shoot = {"next": 3, "until": -1, "start": 0, "x": 0, "y": 0, "dx": 0, "dy": 0}


def draw_shooting_star(cv, frame, c=BLACK):
    """Roughly once every 15 s (24 frames at ~615 ms), from a random heading."""
    if frame >= _shoot["next"] and frame > _shoot["until"]:
        ang = random.uniform(0.0, 6.28318)
        spd = random.randint(18, 28)
        dx = int(spd * math.cos(ang))
        dy = int(spd * math.sin(ang))
        _shoot["dx"] = dx
        _shoot["dy"] = dy
        _shoot["x"] = cv.w // 2 - dx * 4 + random.randint(-30, 30)
        _shoot["y"] = cv.h // 2 - dy * 4 + random.randint(-20, 20)
        _shoot["start"] = frame
        _shoot["until"] = frame + random.randint(9, 13)
        _shoot["next"] = frame + random.randint(18, 30)

    if frame > _shoot["until"]:
        return

    t = frame - _shoot["start"]
    hx = _shoot["x"] + t * _shoot["dx"]
    hy = _shoot["y"] + t * _shoot["dy"]

    tail = 9
    tx = hx - tail * _shoot["dx"] // 4
    ty = hy - tail * _shoot["dy"] // 4
    cv.line(hx, hy, tx, ty, c)
    cv.fill_rect(hx - 1, hy - 1, 3, 3, c)


def draw_tether(cv, frame, x1, y1, c=BLACK):
    """Cubic ease so the line runs along the top edge above the minutes and
    only drops once it is past them. The wave is damped near the anchor so it
    cannot dip into the MM: row."""
    steps = 48
    for t in range(steps + 1):
        f = t / float(steps)
        x = int(TETHER_X0 + (x1 - TETHER_X0) * f)
        y = int(TETHER_Y0 + (y1 - TETHER_Y0) * f * f * f
                + 7 * math.sin(f * 6.5 + frame * 0.45) * f * f)
        cv.fill_rect(x, y, 2, 2, c)


def render(cv, seconds, label, count, frame, animate):
    """Draw the whole face.

    animate=False freezes the scene at frame 0 and suppresses the meteor, so
    idle states produce a byte-identical image and never need a refresh.
    """
    f = frame if animate else 0

    cv.fill(BLACK)
    draw_stars(cv, f, WHITE)

    ax = AX + int(22 * math.sin(f * 0.21))
    ay = AY + int(12 * math.sin(f * 0.5))

    draw_tether(cv, f, ax + 2, ay + 26, WHITE)
    sprites.blit(cv, sprites.ASTRONAUT, ax, ay, SCALE, WHITE)

    # timer: minutes small on top, seconds huge below
    mm, ss = divmod(seconds, 60)
    if mm > 99:
        mm = 99
    CLOCK_FONT.draw(cv, "%02d:" % mm, CLOCK_X, MIN_Y, MIN_SCALE, WHITE)
    CLOCK_FONT.draw(cv, "%02d" % ss, CLOCK_X, SEC_Y, SEC_SCALE, WHITE)

    # small status line, bottom right.
    # Uses the built-in 8x8 font, not font5x7: that one has digits only, so
    # letters would render as blank advances.
    s = "%s-%04d" % (label, count)
    w = cv.text_width(s, STATUS_SCALE)
    cv.text(s, cv.w - w - 3, cv.h - 10, WHITE, STATUS_SCALE)

    if animate:
        draw_shooting_star(cv, frame, WHITE)
