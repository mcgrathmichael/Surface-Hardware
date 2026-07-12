FROM ghcr.io/home-assistant/base-python:3.14-alpine3.24

COPY run.sh /
COPY hardware.py /

RUN chmod a+x /run.sh

CMD ["/run.sh"]