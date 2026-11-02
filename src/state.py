# state.py — the timer state machine, built around espresso.
#
# The pump's vibration is what starts the clock, but locking the portafilter in
# produces a shock of its own. So the sensor is only live in READY: you arm the
# timer after the portafilter is seated, then the pump starts it.
#
#   STANDBY  --press-->  READY     armed; portafilter already seated
#   READY    --press-->  STANDBY   disarm
#   READY    --vibrate-> RUNNING   pump started, session counter bumped
#   RUNNING  --press-->  STOPPED   elapsed frozen
#   STOPPED  --press-->  STANDBY   back to zero
#
# Vibration is ignored in every state except READY.

import time

STANDBY = 0
READY = 1
RUNNING = 2
STOPPED = 3

NAMES = ("STBY", "RDY", "RUN", "STOP")


class Timer:
    def __init__(self):
        self.state = STANDBY
        self.start_ms = 0
        self.elapsed = 0

    def armed(self):
        return self.state == READY

    def running(self):
        return self.state == RUNNING

    def press(self, now):
        """Button press. Returns True if the state changed."""
        if self.state == STANDBY:
            self.state = READY
        elif self.state == READY:
            self.state = STANDBY
        elif self.state == RUNNING:
            self.elapsed = time.ticks_diff(now, self.start_ms) // 1000
            self.state = STOPPED
        elif self.state == STOPPED:
            self.state = STANDBY
            self.elapsed = 0
        return True

    def trigger(self, now):
        """Vibration. Only starts a run from READY. Returns True if started."""
        if self.state != READY:
            return False
        self.state = RUNNING
        self.start_ms = now
        self.elapsed = 0
        return True

    def tick(self, now):
        if self.state == RUNNING:
            self.elapsed = time.ticks_diff(now, self.start_ms) // 1000
        return self.elapsed

    def name(self):
        return NAMES[self.state]
