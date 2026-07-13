#!/usr/bin/with-contenv bashio

echo "Remounting backlight sysfs read-write..."
mount -o remount,rw /sys/class/backlight/intel_backlight
echo "Remount exit code: $?"

mount -o remount,rw /sys 2>/dev/null
echo "Full /sys remount exit code: $?"

export MQTT_HOST=$(bashio::services mqtt "host")
export MQTT_PORT=$(bashio::services mqtt "port")
export MQTT_USER=$(bashio::services mqtt "username")
export MQTT_PASSWORD=$(bashio::services mqtt "password")

echo "Starting Surface Hardware"

python3 /hardware.py