# ruler.py — a 30-second ruler that fills from left to right.
#
# One row only. Ticks every second, longer ticks and a number every 5 s.
# The elapsed part is a solid bar sitting just above the baseline, so the
# current second is readable at a glance without counting ticks.
#
# The ruler covers 0..29 s and is cleared when the 30 s window rolls over;
# total elapsed time lives in the MM:SS counter above it.

import config

BLACK = 0
WHITE = 1

N = config.RULER_SECONDS
STEP = config.RULER_STEP
X0 = config.RULER_X0
Y = config.RULER_Y


class Ruler:
    def __init__(self, cv):
        self.cv = cv

    def x_of(self, i):
        return X0 + i * STEP

    # ---------------------------------------------------------- static

    def template(self):
        """Baseline, ticks and labels. Drawn once per full refresh."""
        cv = self.cv
        cv.hline(X0, Y, N * STEP + 1, BLACK)

        for i in range(N + 1):
            x = self.x_of(i)
            major = (i % config.RULER_LABEL_EVERY == 0)
            cv.vline(x, Y, config.RULER_TICK_MAJOR if major else config.RULER_TICK_MINOR, BLACK)
            if major:
                label = str(i)
                w = len(label) * 8
                cv.text(label, x - w // 2, Y + config.RULER_LABEL_DY, BLACK, 1)

    # ---------------------------------------------------------- dynamic

    def clear(self):
        """Erase the fill bar only, leaving the ruler itself intact."""
        self.cv.fill_rect(X0, Y + config.RULER_FILL_DY, N * STEP + 1,
                          config.RULER_FILL_H, WHITE)

    def fill(self, seconds):
        """Draw the bar for `seconds` elapsed (0..30)."""
        if seconds <= 0:
            return
        if seconds > N:
            seconds = N
        self.cv.fill_rect(X0, Y + config.RULER_FILL_DY,
                          seconds * STEP, config.RULER_FILL_H, BLACK)

    def bounds_of_second(self, i):
        """View-space box covering the bar up to second i, for a windowed refresh."""
        return (X0, Y + config.RULER_FILL_DY, (i + 1) * STEP, config.RULER_FILL_H)
