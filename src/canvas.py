# canvas.py — landscape drawing surface on top of the portrait panel RAM.
#
# The panel's RAM is 122 wide x 250 tall (portrait). Our design is 250 x 122
# (landscape). This class exposes landscape coordinates and maps them onto the
# panel with a 90 degree rotation.
#
# Rotation preserves axis-aligned rectangles, so every rect/hline/vline becomes
# exactly one panel-space fill_rect — no per-pixel work. Only glyphs need
# per-pixel placement, and they are small.
#
# Colour convention follows framebuf: 1 = white, 0 = black.

import math
import framebuf
import config


class Canvas:
    def __init__(self, buf, rotation=None):
        self.fb = framebuf.FrameBuffer(
            buf, config.PANEL_W, config.PANEL_H, framebuf.MONO_HLSB
        )
        self.rot = rotation or config.ROTATION
        self.pw = config.PANEL_W
        self.ph = config.PANEL_H
        self.w = config.VIEW_W
        self.h = config.VIEW_H

    # ------------------------------------------------------------ mapping

    def _pt(self, x, y):
        if self.rot == "cw":
            return self.pw - 1 - y, x
        return y, self.ph - 1 - x

    def _rect(self, x, y, w, h):
        """Map a view rect to the equivalent panel rect (px, py, pw, ph)."""
        if self.rot == "cw":
            return self.pw - (y + h), x, h, w
        return y, self.ph - (x + w), h, w

    # ------------------------------------------------------------ primitives

    def pixel(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            px, py = self._pt(x, y)
            self.fb.pixel(px, py, c)

    def fill_rect(self, x, y, w, h, c):
        if w <= 0 or h <= 0:
            return
        px, py, pw, ph = self._rect(x, y, w, h)
        self.fb.fill_rect(px, py, pw, ph, c)

    def rect(self, x, y, w, h, c):
        if w <= 0 or h <= 0:
            return
        px, py, pw, ph = self._rect(x, y, w, h)
        self.fb.rect(px, py, pw, ph, c)

    def hline(self, x, y, w, c):
        self.fill_rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill_rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        """Bresenham, in view space."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.pixel(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, c)

    def fill_ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            if t < 0:
                continue
            dx = int(rx * math.sqrt(t))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, c)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, c):
        # order the three points by y
        if y0 > y1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        if y1 > y2:
            x1, y1, x2, y2 = x2, y2, x1, y1
        if y0 > y1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        for y in range(y0, y2 + 1):
            if y1 == y0:
                xa = xb = x0
            else:
                xa = x0 + (x1 - x0) * (y - y0) // (y1 - y0)
            if y2 == y0:
                xb = x0
            else:
                xb = x0 + (x2 - x0) * (y - y0) // (y2 - y0)
            if y < y1:
                pass
            elif y1 != y2:
                xa = x1 + (x2 - x1) * (y - y1) // (y2 - y1)
            if xa > xb:
                xa, xb = xb, xa
            self.hline(xa, y, xb - xa + 1, c)

    def fill(self, c):
        self.fb.fill(c)

    def clear(self):
        self.fb.fill(1)

    # ------------------------------------------------------------ text

    def text(self, s, x, y, c, scale=1):
        """8x8 framebuf font, integer-scaled, rotated into place."""
        n = len(s)
        if n == 0:
            return
        tw = n * 8
        tmp = bytearray(((tw + 7) // 8) * 8)
        tfb = framebuf.FrameBuffer(tmp, tw, 8, framebuf.MONO_HLSB)
        tfb.fill(0)
        tfb.text(s, 0, 0, 1)
        for ty in range(8):
            for tx in range(tw):
                if tfb.pixel(tx, ty):
                    self.fill_rect(x + tx * scale, y + ty * scale, scale, scale, c)

    @staticmethod
    def text_width(s, scale=1):
        return len(s) * 8 * scale

    @staticmethod
    def text_height(scale=1):
        return 8 * scale
