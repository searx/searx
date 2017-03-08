FROM alpine:3.5
MAINTAINER searx <https://github.com/asciimoo/searx>
LABEL description "A privacy-respecting, hackable metasearch engine."

ENV BASE_URL=False IMAGE_PROXY=False
EXPOSE 8888
WORKDIR /usr/local/searx
CMD ["/sbin/tini","--","/usr/local/searx/run.sh"]

RUN adduser -D -h /usr/local/searx -s /bin/sh searx searx \
 && echo '#!/bin/sh' >> run.sh \
 && echo 'sed -i "s|base_url : False|base_url : $BASE_URL|g" searx/settings.yml' >> run.sh \
 && echo 'sed -i "s/image_proxy : False/image_proxy : $IMAGE_PROXY/g" searx/settings.yml' >> run.sh \
 && echo 'sed -i "s/ultrasecretkey/`openssl rand -hex 16`/g" searx/settings.yml' >> run.sh \
 && echo 'python searx/webapp.py' >> run.sh \
 && chmod +x run.sh

COPY requirements.txt ./requirements.txt

RUN echo "@commuedge http://nl.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
 && apk -U add \
    build-base \
    python \
    python-dev \
    py-pip \
    libxml2 \
    libxml2-dev \
    libxslt \
    libxslt-dev \
    libffi-dev \
    openssl \
    openssl-dev \
    ca-certificates \
    tini@commuedge \
 && pip install --no-cache -r requirements.txt \
 && apk del \
    build-base \
    python-dev \
    libffi-dev \
    openssl-dev \
    libxslt-dev \
    libxml2-dev \
    openssl-dev \
    ca-certificates \
 && rm -f /var/cache/apk/*

COPY . .

RUN chown -R searx:searx *

USER searx

RUN sed -i "s/127.0.0.1/0.0.0.0/g" searx/settings.yml
