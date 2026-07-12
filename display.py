def screen_on():

    with open(
        "/sys/class/backlight/intel_backlight/bl_power",
        "w"
    ) as f:

        f.write("0")
        def screen_off():
            with open(
        "/sys/class/backlight/intel_backlight/bl_power",
        "w"
    ) as f:

                f.write("1")