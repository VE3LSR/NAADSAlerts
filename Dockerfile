FROM python:3
MAINTAINER projects@ve3lsr.ca

WORKDIR /opt/

ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ADD lib ./lib
ADD run.py .

ENTRYPOINT python3 run.py
