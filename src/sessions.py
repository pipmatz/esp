# sessions.py — persistent timer-session counter on the board's filesystem.
#
# The ESP32-S3 has no battery-backed RTC RAM, but the internal flash filesystem
# survives power cycles, so a tiny text file is enough. Writes are rare (once
# per session), so flash wear is a non-issue.

PATH = "/sessions.txt"


def load():
    try:
        with open(PATH) as f:
            s = f.read().strip()
        return int(s) if s else 0
    except (OSError, ValueError):
        return 0


def save(n):
    try:
        with open(PATH, "w") as f:
            f.write(str(int(n)))
        return True
    except OSError:
        return False


def bump():
    """Increment and persist. Returns the new count."""
    n = load() + 1
    save(n)
    return n


def reset():
    save(0)
