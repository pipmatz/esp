# display.py — panel wrapper: buffer, canvas, and the refresh modes.
#
#   full()    ~2314 ms, flashes black->white, the only mode that removes ghosting
#   base()    ~2314 ms, full refresh that also stores the partial-refresh reference
#   partial() ~607 ms, repaints the whole panel without flashing
#   window()  ~607 ms, repaints one rectangle only (confines ghosting)

import config
import canvas
import epd2in13_V4 as drv


class Display:
    def __init__(self):
        self.buf = bytearray(drv.BUFFER_SIZE)
        self.cv = canvas.Canvas(self.buf)
        self.epd = drv.EPD()

    def init(self):
        self.epd.init()

    def full(self):
        self.epd.display(self.buf)

    def base(self):
        self.epd.displayPartBaseImage(self.buf)

    def partial(self):
        self.epd.displayPartial(self.buf)

    def window(self, x, y, w, h):
        """Refresh only the view-space rect (x, y, w, h)."""
        if w <= 0 or h <= 0:
            return
        px, py, pw, ph = self.cv._rect(x, y, w, h)
        self.epd.displayPartialWindow(self.buf, px, py, px + pw - 1, py + ph - 1)

    def window_box(self, box):
        """Refresh only the view-space box (x, y, w, h)."""
        self.window(box[0], box[1], box[2], box[3])
