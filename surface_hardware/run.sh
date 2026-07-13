#!/usr/bin/with-contenv bashio

echo "Attempting to remount /sys read-write..."
mount -o remount,rw /sys || true

echo "Attempting to remount backlight sysfs read-write..."
mount -o remount,rw /sys/class/backlight/intel_backlight || true

export MQTT_HOST=$(bashio::services mqtt "host")
export MQTT_PORT=$(bashio::services mqtt "port")
export MQTT_USER=$(bashio::services mqtt "username")
export MQTT_PASSWORD=$(bashio::services mqtt "password")

echo "Starting Surface Hardware"

python3 /hardware.py

echo "hardware.py exited — keeping container alive for debugging"
sleep infinity