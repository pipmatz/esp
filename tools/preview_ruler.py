# preview_ruler.py — static preview of the ruler layout.
#
# Shows 23 seconds elapsed: counter 00:23, state RUN, ruler filled to 23.
# Run with:  mpremote run tools/preview_ruler.py

import sys
import time

sys.path.append("/drivers")
sys.path.append("/src")

import config
import display
import ui

d = display.Display()
d.init()
u = ui.UI(d.cv)

u.draw_static()
u.draw_counter(23)
u.draw_state("RUN")
u.draw_ruler(23)

t0 = time.ticks_ms()
d.full()
print("full refresh %d ms" % time.ticks_diff(time.ticks_ms(), t0))
print("ruler x %d..%d, step %d" % (
    config.RULER_X0, config.RULER_X0 + config.RULER_SECONDS * config.RULER_STEP,
    config.RULER_STEP))
