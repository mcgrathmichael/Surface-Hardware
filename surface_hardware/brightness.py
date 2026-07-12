import os

BACKLIGHT = "/sys/class/backlight/intel_backlight"


def exists():
    return os.path.isdir(BACKLIGHT)


def max_brightness():
    with open(f"{BACKLIGHT}/max_brightness") as f:
        return int(f.read().strip())


def get_raw():
    with open(f"{BACKLIGHT}/brightness") as f:
        return int(f.read().strip())


def get():
    maximum = max_brightness()
    current = get_raw()

    return int((current / maximum) * 100)


def set(percent):
    percent = max(0, min(100, int(percent)))

    raw = int(max_brightness() * percent / 100)

    with open(f"{BACKLIGHT}/brightness", "w") as f:
        f.write(str(raw))

    return get()