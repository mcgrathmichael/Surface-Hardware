ARG BUILD_FROM

FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip

COPY run.sh /
COPY hardware.py /

RUN chmod a+x /run.sh

CMD [ "/run.sh" ]