import os

BACKLIGHT = "/sys/class/backlight/intel_backlight"


def supported():
    return os.path.exists(f"{BACKLIGHT}/bl_power")


def screen_on():
    if not supported():
        return False

    with open(f"{BACKLIGHT}/bl_power", "w") as f:
        f.write("0")

    return True


def screen_off():
    if not supported():
        return False

    with open(f"{BACKLIGHT}/bl_power", "w") as f:
        f.write("1")

    return True