FROM alpine:3.12
ENTRYPOINT ["/sbin/tini","--","/usr/local/searx/dockerfiles/docker-entrypoint.sh"]
EXPOSE 8080
VOLUME /etc/searx
VOLUME /var/log/uwsgi

ARG GIT_URL=unknown
ARG VERSION_GITCOMMIT=unknown
ARG SEARX_GIT_VERSION=unknown

ARG SEARX_GID=977
ARG SEARX_UID=977

RUN addgroup -g ${SEARX_GID} searx && \
    adduser -u ${SEARX_UID} -D -h /usr/local/searx -s /bin/sh -G searx searx

ARG TIMESTAMP_SETTINGS=0
ARG TIMESTAMP_UWSGI=0
ARG LABEL_VCS_REF=
ARG LABEL_VCS_URL=

ENV INSTANCE_NAME=searx \
    AUTOCOMPLETE= \
    BASE_URL= \
    MORTY_KEY= \
    MORTY_URL=

WORKDIR /usr/local/searx


COPY requirements.txt ./requirements.txt

RUN apk upgrade --no-cache \
 && apk add --no-cache -t build-dependencies \
    build-base \
    py3-setuptools \
    python3-dev \
    libffi-dev \
    libxslt-dev \
    libxml2-dev \
    openssl-dev \
    tar \
    git \
 && apk add --no-cache \
    ca-certificates \
    su-exec \
    python3 \
    py3-pip \
    libxml2 \
    libxslt \
    openssl \
    tini \
    uwsgi \
    uwsgi-python3 \
    brotli \
 && pip3 install --upgrade pip \
 && pip3 install --no-cache -r requirements.txt \
 && apk del build-dependencies \
 && rm -rf /root/.cache

COPY --chown=searx:searx . .

RUN su searx -c "/usr/bin/python3 -m compileall -q searx"; \
    touch -c --date=@${TIMESTAMP_SETTINGS} searx/settings.yml; \
    touch -c --date=@${TIMESTAMP_UWSGI} dockerfiles/uwsgi.ini; \
    if [ ! -z $VERSION_GITCOMMIT ]; then\
      echo "VERSION_STRING = VERSION_STRING + \"-$VERSION_GITCOMMIT\"" >> /usr/local/searx/searx/version.py; \
    fi; \
    find /usr/local/searx/searx/static -a \( -name '*.html' -o -name '*.css' -o -name '*.js' \
    -o -name '*.svg' -o -name '*.ttf' -o -name '*.eot' \) \
    -type f -exec gzip -9 -k {} \+ -exec brotli --best {} \+

# Keep this argument at the end since it change each time
ARG LABEL_DATE=
LABEL maintainer="searx <${GIT_URL}>" \
      description="A privacy-respecting, hackable metasearch engine." \
      version="${SEARX_GIT_VERSION}" \
      org.label-schema.schema-version="1.0" \
      org.label-schema.name="searx" \
      org.label-schema.version="${SEARX_GIT_VERSION}" \
      org.label-schema.url="${LABEL_VCS_URL}" \
      org.label-schema.vcs-ref=${LABEL_VCS_REF} \
      org.label-schema.vcs-url=${LABEL_VCS_URL} \
      org.label-schema.build-date="${LABEL_DATE}" \
      org.label-schema.usage="https://github.com/searx/searx-docker" \
      org.opencontainers.image.title="searx" \
      org.opencontainers.image.version="${SEARX_GIT_VERSION}" \
      org.opencontainers.image.url="${LABEL_VCS_URL}" \
      org.opencontainers.image.revision=${LABEL_VCS_REF} \
      org.opencontainers.image.source=${LABEL_VCS_URL} \
      org.opencontainers.image.created="${LABEL_DATE}" \
      org.opencontainers.image.documentation="https://github.com/searx/searx-docker"
