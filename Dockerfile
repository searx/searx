FROM debian:stable

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
            python-dev python2.7-minimal python-virtualenv \
            python-pybabel python-pip zlib1g-dev \
            libxml2-dev libxslt1-dev build-essential \
            openssl

RUN useradd searx

WORKDIR /app
RUN pip install uwsgi
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app
RUN sed -i -e "s/ultrasecretkey/`openssl rand -hex 16`/g" searx/settings.yml

EXPOSE 5000
CMD ["/usr/local/bin/uwsgi", "--uid", "searx", "--gid", "searx", "--http", ":5000", "-w",  "searx.webapp"]
