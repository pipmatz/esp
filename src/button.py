# button.py — debounced push button.
#
# The ESP32-S3 dev board's BOOT button is on GPIO 0, active low, with an
# external pull-up. It is the only user-accessible button: RESET/EN reboots
# the chip and cannot be read as a GPIO.
#
# Caveat: holding BOOT while the board powers up enters download mode. As long
# as it is only pressed while running, that never happens.

import time
from machine import Pin

import config


class Button:
    def __init__(self, pin=config.BUTTON_PIN,
                 debounce_ms=config.BUTTON_DEBOUNCE_MS):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.debounce = debounce_ms
        self.raw = 1
        self.stable = 1
        self.changed_at = time.ticks_ms()

    def poll(self):
        """True on a debounced press (high -> low transition)."""
        v = self.pin.value()
        now = time.ticks_ms()

        if v != self.raw:
            self.raw = v
            self.changed_at = now
        elif v != self.stable and time.ticks_diff(now, self.changed_at) >= self.debounce:
            self.stable = v
            if v == 0:
                return True
        return False
