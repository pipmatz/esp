# ui.py — the whole screen layout.
#
#   +--------------------------------------+
#   |              00:23                   |   MM:SS, 4x scale, centred
#   |                                      |
#   |                RUN                   |   state label, 2x scale
#   |                                      |
#   |  #########                           |   fill bar (elapsed)
#   |  |----|----|----|----|----|----|     |   baseline + ticks
#   |  0    5    10   15   20   25   30    |   labels every 5 s
#   +--------------------------------------+

import config
import ruler

BLACK = 0
WHITE = 1


class UI:
    def __init__(self, cv):
        self.cv = cv
        self.ruler = ruler.Ruler(cv)

    # ---------------------------------------------------------- static

    def draw_static(self):
        """Blank screen plus the ruler frame. Needs a full refresh."""
        self.cv.fill(WHITE)
        self.ruler.template()

    # ---------------------------------------------------------- counter

    def counter_bounds(self):
        return (0, config.COUNTER_Y, self.cv.w, 8 * config.COUNTER_SCALE)

    def draw_counter(self, total_seconds):
        m, s = divmod(total_seconds, 60)
        txt = "%02d:%02d" % (m, s)
        cv = self.cv
        x, y, w, h = self.counter_bounds()
        cv.fill_rect(x, y, w, h, WHITE)
        tw = cv.text_width(txt, config.COUNTER_SCALE)
        cv.text(txt, (cv.w - tw) // 2, y, BLACK, config.COUNTER_SCALE)

    # ---------------------------------------------------------- state

    def state_bounds(self):
        return (0, config.STATE_Y, self.cv.w, 8 * config.STATE_SCALE)

    def draw_state(self, label):
        cv = self.cv
        x, y, w, h = self.state_bounds()
        cv.fill_rect(x, y, w, h, WHITE)
        tw = cv.text_width(label, config.STATE_SCALE)
        cv.text(label, (cv.w - tw) // 2, y, BLACK, config.STATE_SCALE)

    # ---------------------------------------------------------- ruler

    def reset_ruler(self):
        self.ruler.clear()

    def draw_ruler(self, seconds_in_window):
        self.ruler.fill(seconds_in_window)
