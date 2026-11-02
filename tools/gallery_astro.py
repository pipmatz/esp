# gallery_astro.py — the timer face, cycling through the four states.
import sys, time
sys.path.append("/drivers"); sys.path.append("/src")
import display, astro

d = display.Display(); cv = d.cv; d.init()

for name, secs in (("STBY", 0), ("RDY", 0), ("STOP", 27)):
    print("=== %s (static)" % name)
    astro.render(cv, secs, name, 1, 0, False)
    d.base()

print("=== RUN (animated)")
for f in range(31):
    astro.render(cv, f, "RUN", 1, f, True)
    if f == 0: d.base()
    else: d.partial()
print("done")
