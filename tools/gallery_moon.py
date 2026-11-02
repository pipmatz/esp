# gallery_moon.py — four lighting variants of a dithered moon.
import sys, time
sys.path.append("/drivers"); sys.path.append("/src")
import display, space

d = display.Display(); cv = d.cv; d.init()

for name, fn in space.VARIANTS:
    print("=== %s" % name)
    t0 = time.ticks_ms()
    fn(cv, 0)
    t1 = time.ticks_ms()
    d.base()
    print("   draw %d ms" % time.ticks_diff(t1, t0))
print("done")
