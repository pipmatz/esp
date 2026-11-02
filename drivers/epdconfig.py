# epdconfig.py — MicroPython hardware layer for the WeAct 2.13" e-paper
#
# Ported from Waveshare's RaspberryPi_JetsonNano epdconfig.py (which talks to
# spidev/gpiozero) to MicroPython's machine.SPI / machine.Pin.
#
# Pins are the ones from PLAN.md §2, chosen to avoid the ESP32-S3 N16R8
# conflicts (GPIO 26-32 flash, 33-37 octal PSRAM, 19/20 native USB).

from machine import Pin, SPI
import time

# --- pin map (must match src/config.py) ---
BUSY_PIN = 4
RST_PIN = 5
DC_PIN = 6
CS_PIN = 7
SCL_PIN = 12
SDA_PIN = 11

SPI_BAUD = 4_000_000

_spi = None
_rst = None
_dc = None
_cs = None
_busy = None


def module_init():
    """Set up SPI and the four control pins. Returns 0 on success."""
    global _spi, _rst, _dc, _cs, _busy
    if _spi is None:
        _spi = SPI(
            1,
            baudrate=SPI_BAUD,
            polarity=0,
            phase=0,
            sck=Pin(SCL_PIN),
            mosi=Pin(SDA_PIN),
        )
        _rst = Pin(RST_PIN, Pin.OUT, value=1)
        _dc = Pin(DC_PIN, Pin.OUT, value=1)
        _cs = Pin(CS_PIN, Pin.OUT, value=1)
        _busy = Pin(BUSY_PIN, Pin.IN)
    return 0


def module_exit():
    """Release the SPI bus and leave the control pins idle."""
    global _spi
    if _spi is not None:
        _spi.deinit()
        _spi = None


def digital_write(pin, value):
    if pin == RST_PIN:
        _rst.value(value)
    elif pin == DC_PIN:
        _dc.value(value)
    elif pin == CS_PIN:
        _cs.value(value)


def digital_read(pin):
    if pin == BUSY_PIN:
        return _busy.value()
    return 0


def delay_ms(ms):
    time.sleep_ms(ms)


def spi_writebyte(data):
    """Write a handful of bytes (list, bytes or bytearray)."""
    _spi.write(bytes(data))


def spi_writebyte2(data):
    """Write a large buffer in one transaction."""
    _spi.write(data)
