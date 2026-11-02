# gallery_standby.py — eight STANDBY entries, each re-rolling the astronaut.
import sys, time
sys.path.append("/drivers"); sys.path.append("/src")
import display, space

d = display.Display(); cv = d.cv; d.init()
for i in range(8):
    print("=== STANDBY entry %d" % (i + 1))
    space.standby(cv, "STBY", i)
    d.base()
print("done")
