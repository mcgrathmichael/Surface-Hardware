ARG BUILD_FROM=ghcr.io/home-assistant/base-python:3.14-alpine3.24

FROM ${BUILD_FROM}

RUN pip install paho-mqtt

COPY rootfs /

COPY hardware.py /usr/bin/hardware.py

RUN chmod a+x /etc/services.d/surface-hardware/run