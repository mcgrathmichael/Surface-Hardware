BACKLIGHT = "/sys/class/backlight/intel_backlight"


def get():
    try:
        with open(f"{BACKLIGHT}/brightness") as f:
            current = int(f.read())

        with open(f"{BACKLIGHT}/max_brightness") as f:
            maximum = int(f.read())

        return int(current * 100 / maximum)

    except Exception:
        return 0



def set(level):

    try:
        level = int(level)

        with open(f"{BACKLIGHT}/max_brightness") as f:
            maximum = int(f.read())

        value = int(maximum * level / 100)

        with open(f"{BACKLIGHT}/brightness", "w") as f:
            f.write(str(value))

    except Exception as e:
        print(
            "Brightness error:",
            e,
            flush=True
        )