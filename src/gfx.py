# gfx.py — shared drawing helpers: dithering and 7-segment digits.

BLACK = 0
WHITE = 1

BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))

# which segments are lit for each digit: a=top b=tr c=br d=bottom e=bl f=tl g=mid
SEGS = {
    "0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc",
    "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg",
    ":": "  ",
}


def dither_rect(cv, x, y, w, h, level):
    """Bayer-dithered fill. level 0 = empty, 16 = solid."""
    for yy in range(y, y + h):
        row = BAYER[yy & 3]
        for xx in range(x, x + w):
            if row[xx & 3] < level:
                cv.pixel(xx, yy, BLACK)


def seg7(cv, d, x, y, w, h, t, on=BLACK, ghost=0, colon=False):
    """One 7-segment glyph. ghost>0 dithers the unlit segments."""
    if colon:
        cv.fill_rect(x + w // 2 - t // 2, y + h // 3, t, t, on)
        cv.fill_rect(x + w // 2 - t // 2, y + 2 * h // 3, t, t, on)
        return

    half = h // 2
    segs = {
        "a": (x + t, y, w - 2 * t, t),
        "b": (x + w - t, y + t, t, half - t - 1),
        "c": (x + w - t, y + half + 1, t, half - t - 1),
        "d": (x + t, y + h - t, w - 2 * t, t),
        "e": (x, y + half + 1, t, half - t - 1),
        "f": (x, y + t, t, half - t - 1),
        "g": (x + t, y + half - t // 2, w - 2 * t, t),
    }
    lit = SEGS.get(d, "")
    for k in ("a", "b", "c", "d", "e", "f", "g"):
        r = segs[k]
        if k in lit:
            cv.fill_rect(r[0], r[1], r[2], r[3], on)
        elif ghost:
            dither_rect(cv, r[0], r[1], r[2], r[3], ghost)
