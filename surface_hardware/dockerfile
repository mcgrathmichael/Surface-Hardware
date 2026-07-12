FROM ghcr.io/home-assistant/base-python:3.14-alpine3.24

RUN apk add --no-cache \
    py3-paho-mqtt

COPY . /app

WORKDIR /app

CMD ["python3","hardware.py"]