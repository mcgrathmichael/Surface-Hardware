#!/usr/bin/with-contenv bashio

echo "Remounting /sys read-write for backlight control"
mount -o remount,rw /sys 2>&1 || echo "WARNING: could not remount /sys rw — screen/brightness control will fail"

export MQTT_HOST=$(bashio::services mqtt "host")
export MQTT_PORT=$(bashio::services mqtt "port")
export MQTT_USER=$(bashio::services mqtt "username")
export MQTT_PASSWORD=$(bashio::services mqtt "password")

echo "Starting Surface Hardware"

python3 /hardware.py