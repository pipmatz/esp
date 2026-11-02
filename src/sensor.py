# sensor.py — SW-420 vibration switch, filtered for "sustained vibration".
#
# The module is an LM393 comparator driving DO: it idles HIGH and pulses LOW
# when the spring contact closes. The onboard pot sets the amplitude threshold,
# but on its own it cannot tell a portafilter knock from a running pump.
#
# What separates them is duration. A knock is one short burst of edges; the
# pump produces a continuous stream. So instead of reacting to a single edge,
# the ISR timestamps every edge and poll() asks "were there at least N edges in
# the last W ms?". A single knock never reaches N; the pump does within a few
# tens of milliseconds.
#
# This adds far less lag than a fixed hold time, because the count is reached
# as soon as enough edges have arrived, not after a fixed delay.

import time
from machine import Pin

import config

RING = 256


class Sensor:
    def __init__(self, pin=config.SENSOR_PIN,
                 edge=config.SENSOR_EDGE,
                 window_ms=config.SENSOR_WINDOW_MS,
                 min_edges=config.SENSOR_MIN_EDGES):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.window = window_ms
        self.min_edges = min_edges
        self.ts = [0] * RING
        self.idx = 0
        self.n = 0

        trigger = Pin.IRQ_FALLING if edge == "falling" else Pin.IRQ_RISING
        self.pin.irq(trigger=trigger, handler=self._isr)

    def _isr(self, _pin):
        self.ts[self.idx] = time.ticks_ms()
        self.idx = (self.idx + 1) % RING
        if self.n < RING:
            self.n += 1

    def recent(self):
        """How many edges landed inside the rolling window."""
        now = time.ticks_ms()
        c = 0
        for i in range(self.n):
            if time.ticks_diff(now, self.ts[i]) <= self.window:
                c += 1
        return c

    def poll(self):
        """True when sustained vibration is detected. Clears the window."""
        if self.recent() >= self.min_edges:
            self.n = 0
            self.idx = 0
            return True
        return False

    def level(self):
        return self.pin.value()
