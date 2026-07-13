#!/usr/bin/env python3
import os
import json
import time

import paho.mqtt.client as mqtt

import brightness
import display

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def read(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return None


def find_backlight():
    base = "/sys/class/backlight"

    try:
        entries = sorted(os.listdir(base))
        if entries:
            return os.path.join(base, entries[0])
    except Exception:
        pass

    return None


BACKLIGHT = find_backlight()


# ------------------------------------------------------------
# MQTT Configuration
# ------------------------------------------------------------

MQTT_HOST = os.getenv("MQTT_HOST", "core-mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="surface_hardware"
)

if MQTT_USER and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

client.reconnect_delay_set(min_delay=1, max_delay=30)

mqtt_connected = False

DEVICE = {
    "identifiers": ["surface_hardware"],
    "name": "Surface Hardware",
    "manufacturer": "Microsoft",
    "model": "Surface Pro"
}


# ------------------------------------------------------------
# MQTT Helpers
# ------------------------------------------------------------

def publish(topic, payload, retain=True):
    if isinstance(payload, (dict, list)):
        payload = json.dumps(payload)

    try:
        client.publish(topic, payload, qos=1, retain=retain)
    except Exception as e:
        # Never let one bad publish stop the rest of discovery/state
        # updates from going out.
        print(f"Publish failed: {topic} -> {e}", flush=True)


def publish_sensor(name, value):
    publish(f"surface_hardware/{name}", value)


# ------------------------------------------------------------
# Home Assistant Discovery
# ------------------------------------------------------------

def publish_discovery():

    sensors = {
        "battery": ("Surface Battery", "%"),
        "cycles": ("Surface Battery Cycles", "cycles"),
        "temperature": ("Surface CPU Temperature", "°C"),
        "brightness": ("Surface Brightness", "%"),
    }

    for key, (name, unit) in sensors.items():
        payload = {
            "name": name,
            "unique_id": f"surface_{key}",
            "state_topic": f"surface_hardware/{key}",
            "unit_of_measurement": unit,
            "device": DEVICE,
        }
        publish(f"homeassistant/sensor/surface_{key}/config", payload)

    # Brightness slider (Number entity)
    brightness_number = {
        "name": "Surface Brightness",
        "unique_id": "surface_brightness_control",
        "command_topic": "surface_hardware/brightness/set",
        "state_topic": "surface_hardware/brightness",
        "min": 0,
        "max": 100,
        "step": 1,
        "mode": "slider",
        "device": DEVICE,
    }
    publish("homeassistant/number/surface_brightness/config", brightness_number)

    # Screen on/off (Switch entity, with real state feedback)
    screen_switch = {
        "name": "Surface Screen",
        "unique_id": "surface_screen_switch",
        "command_topic": "surface_hardware/screen/set",
        "state_topic": "surface_hardware/screen/state",
        "payload_on": "screen_on",
        "payload_off": "screen_off",
        "state_on": "ON",
        "state_off": "OFF",
        "device": DEVICE,
    }
    publish("homeassistant/switch/surface_screen/config", screen_switch)


# ------------------------------------------------------------
# MQTT Callbacks
# ------------------------------------------------------------

def on_connect(client, userdata, flags, reason_code, properties):
    global mqtt_connected
    mqtt_connected = True

    print("MQTT connected", flush=True)

    publish_discovery()
    client.subscribe("surface_hardware/#", qos=1)


def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip()
    print("MQTT COMMAND:", msg.topic, payload, flush=True)

    try:
        if msg.topic == "surface_hardware/brightness/set":
            brightness.set(payload)
            # Optimistic update so the slider doesn't wait up to 30s
            # for the next poll cycle to reflect the new value.
            publish_sensor("brightness", int(float(payload)))

        elif msg.topic == "surface_hardware/screen/set":
            if payload == "screen_on":
                display.screen_on()
                publish("surface_hardware/screen/state", "ON")
            elif payload == "screen_off":
                display.screen_off()
                publish("surface_hardware/screen/state", "OFF")

    except Exception as e:
        print("MQTT command failed:", e, flush=True)


client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_start()


# ------------------------------------------------------------
# Main polling loop
# ------------------------------------------------------------

while True:

    print("----------------------", flush=True)

    if BACKLIGHT:
        maximum = int(read(BACKLIGHT + "/max_brightness") or 1000)
        current = int(read(BACKLIGHT + "/brightness") or 0)
        brightness_pct = int(current * 100 / maximum)

        print(f"Brightness: {brightness_pct} %", flush=True)
        publish_sensor("brightness", brightness_pct)

        # Reflect the real screen power state even if it was changed
        # outside of MQTT (e.g. `echo 1 > .../bl_power` on the host).
        bl_power = read(BACKLIGHT + "/bl_power")
        if bl_power is not None:
            publish("surface_hardware/screen/state", "OFF" if bl_power == "1" else "ON")

    battery = read("/sys/class/power_supply/BAT0/capacity") or "0"
    cycles = read("/sys/class/power_supply/BAT0/cycle_count") or "0"
    temp = read("/sys/class/thermal/thermal_zone1/temp")

    print(f"Battery: {battery} %", flush=True)
    print(f"Cycles: {cycles}", flush=True)

    publish_sensor("battery", battery)
    publish_sensor("cycles", cycles)

    if temp:
        temperature = round(int(temp) / 1000, 1)
        print(f"CPU Temp: {temperature} °C", flush=True)
        publish_sensor("temperature", temperature)

    time.sleep(30)