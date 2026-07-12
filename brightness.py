def get():

    with open("/sys/class/backlight/intel_backlight/actual_brightness") as f:
        return int(f.read())
    
def set(level):

    with open("/sys/class/backlight/intel_backlight/brightness","w") as f:
        f.write(str(level))