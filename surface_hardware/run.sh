#!/usr/bin/with-contenv bashio

echo "Remounting backlight sysfs read-write..."
mount -o remount,rw /sys
echo "Remount exit code: $?"

export MQTT_HOST=$(bashio::services mqtt "host")
export MQTT_PORT=$(bashio::services mqtt "port")
export MQTT_USER=$(bashio::services mqtt "username")
export MQTT_PASSWORD=$(bashio::services mqtt "password")

echo "Starting Surface Hardware"

python3 /hardware.py

echo "hardware.py exited — keeping container alive for debugging"
sleep infinity