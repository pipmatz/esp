# config.py — pins, panel geometry and dial constants.
#
# Everything the rest of the code needs to know about the hardware lives here.

# ---------------------------------------------------------------- pins
# Chosen to avoid ESP32-S3 N16R8 conflicts:
#   GPIO 26-32 flash, 33-37 octal PSRAM, 19/20 native USB, 45/46 strapping
EPD_BUSY = 4
EPD_RST = 5
EPD_DC = 6
EPD_CS = 7
EPD_SCL = 12
EPD_SDA = 11

SENSOR_PIN = 10      # SW-420 DO, falling edge = vibration
BUTTON_PIN = 0       # built-in BOOT, active low

SPI_BAUD = 4_000_000

# ---------------------------------------------------------------- panel
PANEL_W = 122        # native portrait width  (RAM X)
PANEL_H = 250        # native portrait height (RAM Y)

# Our design is landscape: 250 wide x 122 tall.
VIEW_W = PANEL_H     # 250
VIEW_H = PANEL_W     # 122

# Rotation of the view onto the panel.
#   "cw"  : panel must be turned 90 deg clockwise to read the view
#   "ccw" : panel must be turned 90 deg counter-clockwise
ROTATION = "cw"

# ---------------------------------------------------------------- counter
# Big MM:SS at the top, horizontally centred.
COUNTER_SCALE = 4
COUNTER_Y = 10
STATE_SCALE = 2
STATE_Y = 50

# ---------------------------------------------------------------- ruler
# 30 seconds across, one row, 1 px step per second, fills left to right.
RULER_X0 = 20          # x of the 0 s tick
RULER_Y = 82           # baseline y
RULER_STEP = 7         # px per second  -> 30 s spans 210 px (x 20..230)
RULER_SECONDS = 30
RULER_TICK_MINOR = 6   # tick length below the baseline
RULER_TICK_MAJOR = 12
RULER_LABEL_DY = 16    # label offset below the baseline
RULER_LABEL_EVERY = 5  # label every 5 s
RULER_FILL_DY = -10    # fill bar sits this far above the baseline
RULER_FILL_H = 6       # fill bar height

# ---------------------------------------------------------------- timing
REFRESH_FULL_MS = 2400    # measured full refresh
REFRESH_PARTIAL_MS = 615  # measured partial refresh, flat regardless of window

# SW-420 DO idles HIGH and pulses LOW on vibration. If your module is
# inverted, change this to "rising".
SENSOR_EDGE = "falling"

# Sensitivity is about *duration* of vibration, not amplitude: a portafilter
# knock is one short burst, the pump is continuous. So we require several
# edges inside a rolling window rather than reacting to a single one.
#   window_ms  how far back to look
#   min_edges  how many falling edges in that window count as "running"
# Raise min_edges to be less sensitive, lower it for less lag.
SENSOR_WINDOW_MS = 200
SENSOR_MIN_EDGES = 10

BUTTON_DEBOUNCE_MS = 40

# A full refresh clears accumulated ghosting. It flashes the panel for
# ~2.3 s, so keep it rare. Counted in frames (~640 ms each), not seconds, so
# it also runs while idle.
FULL_REFRESH_EVERY_FRAMES = 90     # ~60 s
