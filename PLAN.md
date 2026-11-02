# E-Paper Vibration Timer — Plan

Part 1 of 2. No code yet.

**Repo:** `~/Documents/privat/private_coding/esp/iot` (codeberg `pipmatz/iot`)
**Board:** ESP32-S3-WROOM-1 **N16R8** dev board (16 MB flash, 8 MB octal PSRAM), 2× USB-C
**Display:** WeAct 2.13" e-paper, 250×122, 8-pin header
**Sensor:** SW-420 vibration module (VCC / GND / DO), onboard pot = sensitivity

---

## 1. Behavior

A vibration above the pot threshold starts a timer. The timer runs **endlessly**
(no auto-stop at 180 s). The built-in **BOOT** button toggles:

- 1st press → **stop** (freeze)
- 2nd press → **reset** to zero, back to waiting

Vibrations are ignored while running and while stopped — only a button press
changes state. No extra hardware button; we use the board's BOOT pin (GPIO 0).

The display is a **60-second dial, not digits**, on the left half, plus a
**minute counter digit** on the right half. Total time = minutes (right) +
seconds (dial). The dial's per-second dot fill is the 1 Hz partial-refresh
test — that is where latency and ghosting will show up.

---

## 2. Wiring

All pins chosen to avoid N16R8 conflicts: GPIO 26–32 = flash, GPIO 33–37 =
octal PSRAM, GPIO 19/20 = native USB, GPIO 45/46 = strapping. Everything below
is contiguous on header J1.

| Module | Pin | ESP32-S3 | Note |
|---|---|---|---|
| E-paper | BUSY | GPIO 4 | input |
| E-paper | RES | GPIO 5 | |
| E-paper | D/C | GPIO 6 | |
| E-paper | CS | GPIO 7 | |
| E-paper | SCL | GPIO 12 | = SCK |
| E-paper | SDA | GPIO 11 | = MOSI |
| E-paper | GND | GND | |
| E-paper | VCC | 3V3 | **not 5V** |
| SW-420 | VCC | 3V3 | keeps DO at 3.3 V |
| SW-420 | middle | GND | unlabeled middle pin |
| SW-420 | DO | GPIO 10 | falling-edge IRQ |
| Button | — | GPIO 0 | built-in BOOT, active-low |

**No soldering required.** The e-paper module ships with an FPC ribbon that
breaks out to 8 female jumper sockets; the loose 8-pin header in the box is a
spare for a permanent build later. The ESP32-S3 board's headers are already
soldered. Everything is plug-in.

Pin order is silkscreened on the WeAct board: pin 1 = BUSY … pin 8 = VCC.

Caveats:

- The FPC connector has a flip latch — **open it before inserting the ribbon,
  close it after**. Forcing the ribbon in with the latch closed destroys the
  contacts.
- The ribbon is thin and fragile. Strain-relieve it; don't yank the jumpers.
- Keep SPI leads short (<15 cm); if the panel shows artifacts, drop SPI from
  4 MHz to 2 MHz.

**SW-420 polarity:** DO idles HIGH, pulses LOW on vibration. Verify empirically
in milestone 4 — some batches invert. Debounce with a 300 ms refractory window
(the switch chatters badly).

---

## 3. Display geometry

The circle is constrained by the **short side (122 px)** — never by the width.
Max usable diameter ≈ 112 px (slice dividers at r=56), in either orientation.

### Layout (landscape 250×122)

```
┌─────────────────────────┬──────────────────┐
│                         │                  │
│      DIAL  (122×122)    │   minutes (3×)   │
│      center (61,61)     │   state label    │
│      ring r=52          │   progress bar   │
│                         │                  │
└─────────────────────────┴──────────────────┘
 x: 0..121                 x: 122..249
```

### One ring — 60 dots, 1 dot = 1 second

A single revolution is one minute. At 60 s the ring is full, the minute counter
increments, and the ring starts over.

`radius = 60 × pitch / 2π = 9.549 × pitch`

| radius | pitch | dot | gap |
|---|---|---|---|
| **52** | **5.45 px** | **3 px** | **2.45 px** |

Pixel size ≈ 0.19 mm, so a 3 px dot ≈ 0.57 mm — visible at 30 cm. Diameter
107 px, leaving 7.5 px margin top and bottom.

Angle for second *i*: `θ = −90° + 6°·i`, position
`x = round(61 + 52·cos θ)`, `y = round(61 + 52·sin θ)`.

### Pie slices — 12 sectors of 5 seconds

The dial is divided into **12 sectors of 30°**, one per 5 seconds, by radial
dividers reaching in from the outside edge:

- `θ = −90° + 30°·k`, k = 0…11
- 1 px wide radial line, from **r = 56** (outer edge) inward to **r = 26**
- dividers show in the outer margin and inside the ring, and are interrupted
  wherever a ring dot sits
- the inner disc (r < 26) stays empty — room reserved if we ever want something
  in the middle

**Draw order matters:** dividers → faint template → filled dots. E-paper is
1-bit with no layering, so the ring must be painted *over* the dividers.

**Marker vocabulary — shape, not just size**, so nothing is ambiguous:

| element | rendering | when |
|---|---|---|
| pie-slice divider | 1 px radial line, r=56 → r=26 | 12 lines, every 30° |
| faint template | 1×1 px dot | all 60 ring positions, drawn once |
| elapsed second | 3 px solid square dot | accumulates |

A divider is a line, a counted second is a square — never confusable.

### Right panel

- minutes, 8×8 framebuf font **scaled 3×** → 24 px tall, 1–2 glyphs
- state label (`READY` / `RUN` / `STOP`) scaled 2×
- thin progress bar for the current minute

Note: this counter only changes once per minute, so it is *not* a per-second
ghosting stress test anymore — the dial's 1 Hz dot fill is.

This counter updates every second via **partial refresh** — deliberately the
worst case for ghosting. Its purpose is to let you see how the module behaves.

---

## 4. State machine

```
        ┌──────────┐
        │  READY   │  dial blank, MM:SS = 00:00
        └────┬─────┘
   vibration │
             ▼
        ┌──────────┐
        │  RUNNING │  1 Hz: fill dot, update MM:SS
        └────┬─────┘
             │ press
             ▼
        ┌──────────┐
        │  STOPPED │  frozen, exact MM:SS shown
        └────┬─────┘
             │ press
             └────────► READY (full refresh, t = 0)
```

- Vibration in `STOPPED` or `RUNNING` → ignored
- Press in `READY` → ignored
- The ring fills 0→59 s, then clears and the minute counter increments
- **At 60 s: full panel refresh, ring wiped clean**, next revolution starts;
  minutes keep counting (endless mode)

---

## 5. Toolchain

Nothing is installed yet — no `esptool`, no `mpremote`, no `pyserial`.

```
python3 -m venv .venv
.venv/bin/pip install esptool mpremote pyserial
```

**Firmware:** `ESP32_GENERIC_S3-SPIRAM_OCT` — mandatory. The plain S3 build
cannot see the 8 MB octal PSRAM.

```
esptool.py --chip esp32s3 --port /dev/cu.usbmodem1234561 erase_flash
esptool.py --chip esp32s3 --port /dev/cu.usbmodem1234561 \
  write_flash -z 0 ESP32_GENERIC_S3-SPIRAM_OCT-*.bin
```

Board currently enumerates as `/dev/cu.usbmodem1234561` on the **native
USB-Serial/JTAG** port — single cable, no driver. Deploy with
`mpremote cp src/*.py :` and `mpremote run src/main.py`.

---

## 6. Driver identification

`FPC-A002 20.04.08` is the FPC connector part number, not the controller. The
pin order (`BUSY, RES, D/C, CS, SCL, SDA, GND, VCC`) is the standard
Waveshare/WeAct 2.13" header. At 250×122 exactly two controllers are possible:

| controller | driver | notes |
|---|---|---|
| **SSD1680** | `epd2in13_V4.py` | try first |
| **UC8151D** | `epd2in13_V3.py` | fallback |

Probe procedure: flash a test pattern with V4. Clean image → SSD1680, done.
Garbage / blank / wrong dimensions → V3. Both drivers need `epdconfig.py`
repatching to the pin table in §2.

### RESOLVED (milestone 3)

- **Controller is SSD1680** — `epd2in13_V4` is correct, no V3 fallback needed.
- **Bit order is LSB-first.** Waveshare's CPython driver feeds PIL `'1'`
  `tobytes('raw')`, which is MSB-first; on this panel that renders unreadable
  and mirror-ish. Use `framebuf.MONO_HLSB`, **not** `MONO_HMSB`.
  Found with `tools/driver_probe2.py` (five bands, one pre-transform each).
- **No mirror, no vertical flip** — panel top-left is RAM top-left.
- **Full refresh ≈ 2313 ms**, measured.

### Landscape rotation

The panel is natively **portrait 122×250**; our design is **landscape 250×122**.
So the drawing layer maps landscape → panel with a 90° rotation. Axis-aligned
rectangles stay axis-aligned under rotation, so `fill_rect` maps to a single
panel-space `fill_rect` — no per-pixel work for the dial or the progress bar.
Only glyphs need per-pixel placement.

**Known quirk:** the V4 MicroPython driver's partial refresh needs
`init(0)` → `init(1)` before `displayPartial()`, and its partial LUT is
fragile. Budget time for this in milestone 6.

---

## 7. Repo layout

```
esp/iot/
├── PLAN.md
├── README.md
├── .gitignore            # .venv/, firmware/*.bin, __pycache__/
├── firmware/             # MicroPython .bin (gitignored)
├── drivers/
│   ├── epd2in13_V4.py
│   ├── epd2in13_V3.py
│   └── epdconfig.py      # patched to §2 pins
├── src/
│   ├── config.py         # pins, geometry constants, timings
│   ├── main.py           # entry point, main loop
│   ├── display.py        # panel wrapper: full/partial refresh
│   ├── dial.py           # ring geometry + drawing
│   ├── digits.py         # 8×8 font scaling, MM:SS
│   ├── sensor.py         # SW-420 IRQ + refractory window
│   ├── button.py         # BOOT debounce
│   └── state.py          # state machine
└── tools/
    ├── flash.sh
    ├── deploy.sh
    └── driver_probe.py   # test pattern for controller ID
```

---

## 8. Build & test order

Each milestone is independently verifiable — don't proceed on a red one.

| # | Milestone | Pass criterion |
|---|---|---|
| 0 | venv + `esptool`/`mpremote` | `mpremote connect list` sees the board |
| 1 | Flash MicroPython SPIRAM_OCT | REPL prompt, `esp.flash_size()` = 16 MB |
| 2 | Plug in FPC ribbon + 8 jumpers | — |
| 3 | **Driver probe** | a clean test pattern on the panel |
| 4 | SW-420 on GPIO 10 | DO polarity confirmed, pot sets a usable threshold |
| 5 | BOOT button debounce | exactly one event per press |
| 6 | Static dial (full refresh) | 12 slice dividers, 60 faint marks, ring at r=52 |
| 7 | **1 Hz partial refresh of the dial dot** | measure latency + ghost growth over one 60 s revolution |
| 8 | Integrate state machine | vibration → run → press → stop → press → reset |
| 9 | 60 s revolution | ring wipes clean, minute counter increments |
| 10 | Commit | clean tree, README updated |

Milestone 3 is the gate: until the controller is identified, nothing else can be
trusted. Milestone 7 is the measurement you asked for.

---

## 9. Risks

| risk | mitigation |
|---|---|
| Controller is neither SSD1680 nor UC8151D | probe step; fall back to raw SPI init sequence |
| V4 partial-refresh LUT quirks | try V3 driver; worst case full-refresh at 1 Hz (slow, ~2 s) |
| SW-420 chatter → multiple starts | 300 ms refractory window + IRQ disable during handler |
| Jumper leads too long at 4 MHz | drop to 2 MHz |
| 60 s full refresh blinks whole panel ~2 s | rare in practice: 95 % of runs are sub-minute |
| FPC ribbon damaged by latch mishandling | open latch before insert; spare header exists if the ribbon dies |
| Holding BOOT during reset → download mode | never hold at power-up; debounce in software |

---

## 10. Resolved decisions

**A. 60 s clean → full panel refresh.** The panel flashes black→white→redraw
for ~2 s once per minute of running time. Accepted: it is the only refresh that
actually removes ghosting, and 95 % of runs never reach it.

**B. Dial → one ring, 60 dots, outside-in pie slices.** r=52, 3 px dots,
divided into 12 five-second sectors by radial dividers (r=56 → r=26). At 60 s
the full refresh wipes the ring and the minute counter increments. Dropped:
the three concentric rings and the separate minute ring.
