# gallery4.py — 15 iterations of the five chosen directions.
#
# Run with:  mpremote run tools/gallery4.py
#
# 10 frames per design, counter advancing 4 s per frame. Order:
#
#   SPIRAL1 SPIRAL2 SPIRAL3   rotating / progressive / comet spiral
#   TERM1   TERM2   TERM3     terminal, session count, wall clock
#   ASTRO1  ASTRO2  ASTRO3    astronaut on moon / floating / walking
#   ROCKET1 ROCKET2 ROCKET3   cruise / boost / descent
#   PAC1    PAC2    PAC3      pac-man, white on black
#
# Set the RTC first so the terminal faces show a real time:
#   ./tools/settime.sh

import sys
import time

sys.path.append("/drivers")
sys.path.append("/src")

import display
import designs4
import sessions

FRAMES = 10

d = display.Display()
cv = d.cv
d.init()

print("sessions on flash: %d" % sessions.load())

_times = []

for name, fn in designs4.DESIGNS:
    print("=== %s" % name)
    for f in range(FRAMES):
        fn(cv, 0, f * 4, f)
        t0 = time.ticks_ms()
        if f == 0:
            d.base()
        else:
            d.partial()
        _times.append(time.ticks_diff(time.ticks_ms(), t0))

print("frames: %d  avg: %d ms" % (len(_times), sum(_times) // len(_times)))
