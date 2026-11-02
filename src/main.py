# main.py — espresso timer.
#
# The pump's vibration starts the clock, but the portafilter lock-in produces a
# shock too, so the sensor is only live in READY. Arm it after seating the
# portafilter, then the pump starts the run.
#
#   STANDBY  --press-->  READY     armed
#   READY    --press-->  STANDBY   disarm
#   READY    --vibrate-> RUNNING   session counter bumped
#   RUNNING  --press-->  STOPPED   elapsed frozen
#   STOPPED  --press-->  STANDBY   back to zero
#
# The screen is only refreshed when something actually changes. While running
# that is every frame (the animation); while idle it is only on a state change,
# which keeps the panel quiet and ghost-free.

import sys

sys.path.append("/drivers")
sys.path.append("/src")

import time

import config
import display
import astro
import space
import sessions
import sensor
import button
import state


def run(limit=None):
    d = display.Display()
    d.init()
    cv = d.cv

    timer = state.Timer()
    sen = sensor.Sensor()
    btn = button.Button()
    count = sessions.load()

    frame = 0
    iters = 0
    dirty = True
    last_full_frame = 0

    print("espresso timer up, sessions=%d" % count)

    while limit is None or iters < limit:
        iters += 1
        now = time.ticks_ms()

        # ---- inputs
        if sen.poll() and timer.trigger(now):
            count = sessions.bump()
            dirty = True

        if btn.poll():
            timer.press(now)
            dirty = True

        secs = timer.tick(now)

        # ---- render only when there is something new to show
        if timer.running():
            astro.render(cv, secs, timer.name(), count, frame, True)
            if frame - last_full_frame >= config.FULL_REFRESH_EVERY_FRAMES:
                d.full()
                last_full_frame = frame
            else:
                d.partial()
            frame += 1
            dirty = False
        elif dirty:
            if timer.state == state.STANDBY:
                # re-rolls the astronaut's position on every entry
                space.standby(cv, timer.name(), count)
            else:
                astro.render(cv, secs, timer.name(), count, 0, False)
            d.base()
            frame = 0
            last_full_frame = 0
            dirty = False
        else:
            time.sleep_ms(40)


if __name__ == "__main__":
    run()
