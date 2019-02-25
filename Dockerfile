FROM python:3
MAINTAINER projects@ve3lsr.ca

# RUN apt-get update && apt-get install -yq git && apt-get clean && rm -rf /var/lib/apt/lists/* /var/tmp/* /tmp/*

WORKDIR /opt/

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD lib ./lib
ADD run.py .

ENTRYPOINT python3 run.py
