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


# ------------------------------------------------------------
# MQTT Helpers
# ------------------------------------------------------------

def publish(topic, payload, retain=True):
    if isinstance(payload, (dict, list)):
        payload = json.dumps(payload)

    client.publish(topic, payload, qos=1, retain=retain)


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
            "device": {
                "identifiers": ["surface_hardware"],
                "name": "Surface Hardware",
                "manufacturer": "Microsoft",
                "model": "Surface Pro"
            }
        }
        publish(f"homeassistant/sensor/surface_{key}/config", payload)

    brightness_number = {
        "name": "Surface Brightness",
        "unique_id": "surface_brightness_control",
        "command_topic": "surface_hardware/brightness/set",
        "state_topic": "surface_hardware/brightness",
        "min": 0,
        "max": 100,
        "step": 1,
        "mode": "slider"
    }
    publish("homeassistant/number/surface_brightness/config", brightness_number)

    for state, command in (("On", "screen_on"), ("Off", "screen_off")):
        payload = {
            "name": f"Surface Screen {state}",
            "unique_id": f"surface_screen_{state.lower()}",
            "command_topic": "surface_hardware/screen",
            "payload_press": command
        }
        publish(f"homeassistant/button/surface_screen_{state.lower()}/config", payload)


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

        elif msg.topic == "surface_hardware/screen":
            if payload == "screen_on":
                display.screen_on()
            elif payload == "screen_off":
                display.screen_off()

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