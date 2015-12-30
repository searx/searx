FROM alpine:3.3
MAINTAINER Wonderfall <wonderfall@opmbx.org>

ENV BASE_URL=False IMAGE_PROXY=False

COPY . /usr/local/searx

RUN apk -U add \
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
 && adduser -D -h /usr/local/searx -s /bin/sh searx searx \
 && cd /usr/local/searx \
 && pip install --no-cache -r requirements.txt \
 && sed -i "s/127.0.0.1/0.0.0.0/g" searx/settings.yml \
 && sed -i "s/ultrasecretkey/`openssl rand -hex 16`/g" searx/settings.yml \
 && sed -i "s|base_url : False|base_url : $BASE_URL|g" searx/settings.yml \
 && sed -i "s/image_proxy : False/image_proxy : $IMAGE_PROXY/g" searx/settings.yml \
 && apk del \
    build-base \
    python-dev \
    py-pip\
    libffi-dev \
    openssl-dev \
    libxslt-dev \
    libxml2-dev \
    openssl-dev \
    ca-certificates \
 && chown -R searx:searx /usr/local/searx \
 && rm -f /var/cache/apk/*

EXPOSE 8888
USER searx
WORKDIR /usr/local/searx
CMD ["python", "searx/webapp.py"]
