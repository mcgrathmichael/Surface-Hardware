ARG BUILD_FROM

FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip

RUN pip3 install --no-cache-dir paho-mqtt

COPY run.sh /run.sh
COPY hardware.py /usr/bin/hardware.py
COPY brightness.py /usr/bin/brightness.py
COPY display.py /usr/bin/display.py

RUN chmod +x /run.sh
RUN chmod +x /usr/bin/hardware.py

CMD [ "/run.sh" ]