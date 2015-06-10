FROM python:2.7-slim

WORKDIR /app

RUN useradd searx

EXPOSE 5000
CMD ["/usr/local/bin/uwsgi", "--uid", "searx", "--gid", "searx", "--http", ":5000", "-w",  "searx.webapp"]

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
            zlib1g-dev libxml2-dev libxslt1-dev libffi-dev build-essential \
            libssl-dev openssl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache uwsgi

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache -r requirements.txt

COPY . /app
RUN sed -i -e "s/ultrasecretkey/`openssl rand -hex 16`/g" searx/settings.yml
