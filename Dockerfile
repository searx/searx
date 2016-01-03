FROM alpine:3.3

ENV BASE_URL=False IMAGE_PROXY=False

EXPOSE 8888

WORKDIR /usr/local/searx

CMD ["./run.sh"]

RUN adduser -D -h /usr/local/searx -s /bin/sh searx searx \
 && echo '#!/bin/sh' >> run.sh \
 && echo 'sed -i "s|base_url : False|base_url : $BASE_URL|g" searx/settings.yml' >> run.sh \
 && echo 'sed -i "s/image_proxy : False/image_proxy : $IMAGE_PROXY/g" searx.setting.yml' >> run.sh \
 && echo 'python searx/webapp.py' >> run.sh \
 && chmod +x run.sh

COPY requirements.txt /usr/local/searx/requirements.txt

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
 && pip install --no-cache -r /usr/local/searx/requirements.txt \
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
 && rm -f /var/cache/apk/*

COPY . /usr/local/searx

RUN chown -R searx:searx /usr/local/searx

USER searx

RUN cd /usr/local/searx \
 && sed -i "s/127.0.0.1/0.0.0.0/g" searx/settings.yml \
 && sed -i "s/ultrasecretkey/`openssl rand -hex 16`/g" searx/settings.yml
