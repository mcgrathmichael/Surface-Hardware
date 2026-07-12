import time
import os


def read_file(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception as e:
        return str(e)


print("Surface Hardware started")

while True:

    print("--------------------")

    print(
        "Brightness:",
        read_file(
            "/sys/class/backlight/intel_backlight/actual_brightness"
        )
    )

    print(
        "Battery:",
        read_file(
            "/sys/class/power_supply/BAT0/capacity"
        )
    )

    print(
        "Cycles:",
        read_file(
            "/sys/class/power_supply/BAT0/cycle_count"
        )
    )

    print(
        "CPU:",
        read_file(
            "/sys/class/thermal/thermal_zone1/temp"
        )
    )

    time.sleep(30)