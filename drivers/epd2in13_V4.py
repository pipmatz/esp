# epd2in13_V4.py — MicroPython port of the Waveshare SSD1680 2.13" driver
#
# Original: Waveshare epd2in13_V4.py V1.0 (2023-06-25), CPython/PIL.
# Changes for MicroPython:
#   * no PIL — callers hand in a raw bytearray (see src/display.py)
#   * no logging
#   * ReadBusy() has a timeout instead of spinning forever
#   * module_init() is called explicitly by init(), not per refresh
#
# Panel is natively PORTRAIT: 122 wide x 250 tall, 1 bit/pixel, MSB first,
# bit set = white. RAM needs 16 bytes per row (122 px -> ceil(122/8)).

import epdconfig

EPD_WIDTH = 122
EPD_HEIGHT = 250

# 16 bytes per row * 250 rows
BUFFER_SIZE = ((EPD_WIDTH + 7) // 8) * EPD_HEIGHT

BLACK = 0x00
WHITE = 0xFF


class EPD:
    def __init__(self):
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN

    # ---------- low level ----------

    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20)
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(2)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20)

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data2(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte2(data)
        epdconfig.digital_write(self.cs_pin, 1)

    def ReadBusy(self, timeout_ms=15000):
        """Block until BUSY goes low (0 = idle, 1 = busy)."""
        waited = 0
        while epdconfig.digital_read(self.busy_pin) == 1:
            epdconfig.delay_ms(10)
            waited += 10
            if waited >= timeout_ms:
                raise OSError("e-paper BUSY timeout")

    # ---------- window / cursor ----------

    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44)  # SET_RAM_X_ADDRESS_START_END_POSITION
        # x must be a multiple of 8, low 3 bits are ignored
        self.send_data((x_start >> 3) & 0xFF)
        self.send_data((x_end >> 3) & 0xFF)

        self.send_command(0x45)  # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    def SetCursor(self, x, y):
        self.send_command(0x4E)  # SET_RAM_X_ADDRESS_COUNTER
        self.send_data(x & 0xFF)
        self.send_command(0x4F)  # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)

    # ---------- update sequences ----------

    def TurnOnDisplay(self):
        self.send_command(0x22)
        self.send_data(0xF7)
        self.send_command(0x20)
        self.ReadBusy()

    def TurnOnDisplay_Fast(self):
        self.send_command(0x22)
        self.send_data(0xC7)
        self.send_command(0x20)
        self.ReadBusy()

    def TurnOnDisplayPart(self):
        self.send_command(0x22)
        self.send_data(0xFF)
        self.send_command(0x20)
        self.ReadBusy()

    # ---------- init ----------

    def init(self):
        epdconfig.module_init()
        self.reset()

        self.ReadBusy()
        self.send_command(0x12)  # SWRESET
        self.ReadBusy()

        self.send_command(0x01)  # Driver output control
        self.send_data(0xF9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11)  # Data entry mode: X+, Y+
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)

        self.send_command(0x3C)  # Border waveform
        self.send_data(0x05)

        self.send_command(0x21)  # Display update control
        self.send_data(0x00)
        self.send_data(0x80)

        self.send_command(0x18)  # Temperature sensor
        self.send_data(0x80)

        self.ReadBusy()
        return 0

    def init_fast(self):
        epdconfig.module_init()
        self.reset()

        self.send_command(0x12)  # SWRESET
        self.ReadBusy()

        self.send_command(0x18)  # Read built-in temperature sensor
        self.send_command(0x80)

        self.send_command(0x11)  # Data entry mode
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)

        self.send_command(0x22)
        self.send_data(0xB1)
        self.send_command(0x20)
        self.ReadBusy()

        self.send_command(0x1A)  # Write to temperature register
        self.send_data(0x64)
        self.send_data(0x00)

        self.send_command(0x22)
        self.send_data(0x91)
        self.send_command(0x20)
        self.ReadBusy()
        return 0

    # ---------- drawing ----------

    def display(self, image):
        """Full refresh from a raw panel buffer."""
        self.send_command(0x24)
        self.send_data2(image)
        self.TurnOnDisplay()

    def display_fast(self, image):
        self.send_command(0x24)
        self.send_data2(image)
        self.TurnOnDisplay_Fast()

    def displayPartBaseImage(self, image):
        """Store image as both RAM and the partial-refresh reference."""
        self.send_command(0x24)
        self.send_data2(image)
        self.send_command(0x26)
        self.send_data2(image)
        self.TurnOnDisplay()

    def displayPartial(self, image):
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(1)
        epdconfig.digital_write(self.reset_pin, 1)

        self.send_command(0x3C)  # Border waveform
        self.send_data(0x80)

        self.send_command(0x01)  # Driver output control
        self.send_data(0xF9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11)  # Data entry mode
        self.send_data(0x03)

        self.SetWindow(0, 0, self.width - 1, self.height - 1)
        self.SetCursor(0, 0)

        self.send_command(0x24)  # WRITE_RAM
        self.send_data2(image)
        self.TurnOnDisplayPart()

    def displayPartialWindow(self, image, x0, y0, x1, y1):
        """Partial refresh of one rectangle only.

        x0/x1 are pixel columns (rounded down to a byte boundary), y0/y1 are
        rows. Only that region is rewritten and repainted, so ghosting is
        confined to it and the update is much faster than a full-panel one.

        `image` is still the full-panel buffer; the window is sliced out of it.
        """
        xb0 = x0 >> 3
        xb1 = x1 >> 3
        nbytes = xb1 - xb0 + 1
        rows = y1 - y0 + 1
        row_bytes = (self.width + 7) // 8

        out = bytearray(nbytes * rows)
        i = 0
        for y in range(y0, y1 + 1):
            off = y * row_bytes + xb0
            out[i:i + nbytes] = image[off:off + nbytes]
            i += nbytes

        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(1)
        epdconfig.digital_write(self.reset_pin, 1)

        self.send_command(0x3C)  # Border waveform
        self.send_data(0x80)

        self.send_command(0x01)  # Driver output control
        self.send_data(0xF9)
        self.send_data(0x00)
        self.send_data(0x00)

        self.send_command(0x11)  # Data entry mode
        self.send_data(0x03)

        self.SetWindow(xb0 << 3, y0, (xb1 << 3) + 7, y1)
        self.SetCursor(xb0 << 3, y0)

        self.send_command(0x24)  # WRITE_RAM
        self.send_data2(out)
        self.TurnOnDisplayPart()

    def Clear(self, color=WHITE):
        linewidth = (self.width + 7) // 8
        self.send_command(0x24)
        self.send_data2(bytearray([color]) * (self.height * linewidth))
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10)  # Deep sleep
        self.send_data(0x01)
        epdconfig.delay_ms(2000)
        epdconfig.module_exit()
