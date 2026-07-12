import time


def read(path):
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception as e:
        return f"ERROR {e}"


print("Surface Hardware started", flush=True)


while True:

    print("----------------------", flush=True)

    print(
        "Brightness:",
        read("/sys/class/backlight/intel_backlight/actual_brightness"),
        flush=True
    )

    print(
        "Battery:",
        read("/sys/class/power_supply/BAT0/capacity"),
        flush=True
    )

    print(
        "Cycles:",
        read("/sys/class/power_supply/BAT0/cycle_count"),
        flush=True
    )

    print(
        "CPU temp:",
        read("/sys/class/thermal/thermal_zone1/temp"),
        flush=True
    )

    time.sleep(30)