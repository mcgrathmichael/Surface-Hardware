ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    py3-paho-mqtt

COPY rootfs/usr/bin/ /usr/bin/

RUN chmod +x /usr/bin/hardware.py