# ###################################
# # AlertManager Discord BOT Dockerfile
# #
# # Version: 0.1
# # Author:  Attilio Greco attilio.greco.gapmilano@gmail.com
# ###################################
# 
FROM alpine:latest as runtime
RUN apk add --no-cache --virtual .build-deps gcc musl-dev python3-dev libffi-dev libressl-dev pcre-dev
RUN apk add --no-cache python3 \
  uwsgi \
  uwsgi-python3 \
  uwsgi-http \
  uwsgi-gevent

RUN apk add --no-cache --update
RUN adduser app -h /opt/app/ -u 1100 -D -S -G uwsgi -s /sbin/nologin

RUN python3 -m venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . /opt/app
WORKDIR /opt/app
RUN pip3 install -r requirements.txt
RUN apk del .build-deps gcc musl-dev python3-dev libffi-dev libressl-dev pcre-dev

EXPOSE 8080

# Define default command.
CMD ["/usr/sbin/uwsgi", "/opt/app/uwsgi.ini"]
