# font5x7.py — chunky 5x7 pixel font, integer-scalable.
#
# Hand-drawn so the digits look deliberate at 1-bit, unlike the blocky 8x8
# framebuf font. Every glyph is 5 wide, 7 tall, one blank column of spacing.

GLYPHS = {
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    ":": (".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}

W = 5
H = 7
ADVANCE = 6


def width(s, scale=1):
    return len(s) * ADVANCE * scale - scale


def draw(cv, s, x, y, scale=1, c=0, dots=False, dsize=1):
    """Draw string s.

    dots=True renders each font pixel as a dot of `dsize` px on a `scale` px
    pitch, for a dot-matrix / LED look. dots=False renders solid blocks.
    """
    cx = x
    for ch in s:
        g = GLYPHS.get(ch)
        if g is not None:
            for ry in range(H):
                row = g[ry]
                for rx in range(W):
                    if row[rx] == "#":
                        if dots:
                            cv.fill_rect(cx + rx * scale, y + ry * scale,
                                         dsize, dsize, c)
                        else:
                            cv.fill_rect(cx + rx * scale, y + ry * scale,
                                         scale, scale, c)
        cx += ADVANCE * scale
    return cx


def draw_centred(cv, s, y, scale=1, c=0, dots=False, dsize=1):
    draw(cv, s, (cv.w - width(s, scale)) // 2, y, scale, c, dots, dsize)
