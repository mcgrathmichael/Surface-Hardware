FROM ghcr.io/home-assistant/amd64-base:3.24

RUN apk add --no-cache \
    python3 \
    py3-paho-mqtt

COPY rootfs/usr/bin/ /usr/bin/

RUN chmod +x /usr/bin/hardware.py

CMD ["/usr/bin/hardware.py"]