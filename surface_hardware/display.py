BACKLIGHT = "/sys/class/backlight/intel_backlight"


def screen_on():

    try:
        with open(
            f"{BACKLIGHT}/bl_power",
            "w"
        ) as f:
            f.write("0")

    except Exception as e:
        print(
            "Screen on error:",
            e,
            flush=True
        )



def screen_off():

    try:
        with open(
            f"{BACKLIGHT}/bl_power",
            "w"
        ) as f:
            f.write("1")

    except Exception as e:
        print(
            "Screen off error:",
            e,
            flush=True
        )