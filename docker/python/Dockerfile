FROM python:3.9-slim

# inserir o log do python no log do docker
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y python-dev-is-python3 libpq-dev libssl-dev build-essential git-core libldap2-dev libsasl2-dev libfontconfig1 libxrender1 libfreetype6-dev ffmpeg cron

RUN mkdir -p /app/src/requirements/

ADD requirements/ /app/src/requirements/

ARG requirements=production

RUN pip install --upgrade pip

RUN pip install --upgrade distlib

RUN pip install --upgrade setuptools

RUN pip install -r /app/src/requirements/$requirements.txt
