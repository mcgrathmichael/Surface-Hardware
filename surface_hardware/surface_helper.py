import os
import time

import paho.mqtt.client as mqtt

BACKLIGHT = "/sys/class/backlight/intel_backlight"

MQTT_HOST = os.getenv("MQTT_HOST", "core-mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")


def set_brightness(value):
    try:
        with open(f"{BACKLIGHT}/max_brightness") as f:
            maximum = int(f.read().strip())

        raw = int(maximum * float(value) / 100)

        with open(f"{BACKLIGHT}/brightness", "w") as f:
            f.write(str(raw))

        print(f"Brightness set to {value}% ({raw})", flush=True)
    except Exception as e:
        print("Brightness error:", e, flush=True)


def set_screen(power):
    try:
        with open(f"{BACKLIGHT}/bl_power", "w") as f:
            f.write("1" if power == "screen_off" else "0")

        print(f"Screen -> {power}", flush=True)
    except Exception as e:
        print("Screen error:", e, flush=True)


def on_connect(client, userdata, flags, reason_code, properties):
    print("MQTT connected (surface_helper)", flush=True)
    client.subscribe("surface_hardware/brightness/set")
    client.subscribe("surface_hardware/screen/set")


def on_message(client, userdata, msg):
    payload = msg.payload.decode().strip()
    print("Helper received:", msg.topic, payload, flush=True)

    if msg.topic == "surface_hardware/brightness/set":
        set_brightness(payload)
        client.publish("surface_hardware/brightness", int(float(payload)), retain=True)

    elif msg.topic == "surface_hardware/screen/set":
        set_screen(payload)
        state = "OFF" if payload == "screen_off" else "ON"
        client.publish("surface_hardware/screen/state", state, retain=True)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="surface_helper")

if MQTT_USER and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

client.reconnect_delay_set(min_delay=1, max_delay=30)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)
client.loop_forever()
