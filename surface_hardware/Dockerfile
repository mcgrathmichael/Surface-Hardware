ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python
RUN apk add --no-cache \
        python3 \
        py3-pip

# Alpine 3.19+ marks system Python as "externally managed" (PEP 668).
RUN pip3 install --no-cache-dir --break-system-packages paho-mqtt

# Add-on files
COPY run.sh /run.sh
COPY hardware.py /hardware.py
COPY brightness.py /brightness.py
COPY display.py /display.py

RUN chmod a+x /run.sh /hardware.py

CMD [ "/run.sh" ]