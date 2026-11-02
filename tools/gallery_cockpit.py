# gallery_cockpit.py — five STANDBY cockpit screens.
# Run with:  mpremote run tools/gallery_cockpit.py

import sys
import time

sys.path.append("/drivers")
sys.path.append("/src")

import display
import cockpit

d = display.Display()
cv = d.cv
d.init()

for name, fn in cockpit.DESIGNS:
    print("=== %s" % name)
    fn(cv, 0)
    cockpit.render(cv, "STBY", 0)
    t0 = time.ticks_ms()
    d.base()
    print("   drawn in %d ms" % time.ticks_diff(time.ticks_ms(), t0))
print("done")
