#!/usr/bin/env python3

import colorlog
import logging
import pynaads
import pyax25
import json
import time
from elasticsearch import Elasticsearch
import hashlib
import crcmod
import yaml

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger.addHandler(handler)

class Alerting():
    def __init__(self, config=False):
        self.esItems = []
        if config == False:
            with open("config.yml", 'r') as ymlfile:
                self.cfg = yaml.load(ymlfile)
        else:
            self.cfg = config

        self.geopoints = [tuple(map(float,e.split(','))) for e in self.cfg['naads']['geopoints']]

        self.p = pynaads.naads(passhb=False)

        if self.cfg['ax25']['enabled']:
            self.x = pyax25.AX25(self.cfg['ax25']['call'], self.cfg['ax25']['ip_address'], self.cfg['ax25']['port'], self.cfg['ax25']['ssid'])
            self.x.setDst(self.cfg['ax25']['dest'])
            for relay in self.cfg['ax25']['relays']:
                self.x.addRelay(relay.split(',')[0], int(relay.split(',')[1]))

        if self.cfg['elasticsearch']['enabled']:
            self.es = Elasticsearch(self.cfg['elasticsearch']['host_url'])

        self.p.connect()
        self.p.start()
        self.sendAX("VE3LSR Weather Alerting Started")

    def clcMap(self, q):
        if q['geocode']['layer:EC-MSC-SMC:1.0:CLC'][0] in self.cfg['ax25']['mappings']:
            zone = "WX{}".format(self.cfg['ax25']['mappings'][q['geocode']['layer:EC-MSC-SMC:1.0:CLC'][0]])
        else:
            zone = "WX00"
        return zone

    def sendAX(self, message, zone=""):
        logger.info("Bulletin: {}, Group: {}".format(message, zone))
        if self.cfg['ax25']['enabled']:
            try:
                self.x.sendBulletin(message, "{}".format(zone))
            except:
                logger.error("Error sending AX25 message")

    def elasticAdd(self, event):
        self.esItems.append({'index': {'_id': event['id']}})
        self.esItems.append(event)

    def elasticSend(self):
        if self.cfg['elasticsearch']['enabled']:
            self.es.bulk(index="naads", doc_type="_doc", body=self.esItems)
        self.esItems = []

    def sendAlerts(self, alert):
        zone = self.clcMap(alert)
        # cap-pac@canada.ca are weather alerts, we can treat them all the same
        if alert['sender'] == "cap-pac@canada.ca":
            self.sendAX("{}: {} - {}".format(alert['msgType'], alert['areaDesc'], alert['headline']), zone)
        # Amber Alerts
        elif alert['eventCode']['profile:CAP-CP:Event:0.4'] == 'amber':
            self.sendAX("{}: {} - {}: {}".format(alert['event'], alert['areaDesc'], alert['headline'], alert['parameter']['layer:SOREM:2.0:WirelessText']), 'AMBR')
        # All other alerts
        else:
            if 'layer:SOREM:2.0:WirelessText' in alert['parameter']:
                self.sendAX("{}: {} - {}: {}".format(alert['event'], alert['areaDesc'], alert['headline'], alert['parameter']['layer:SOREM:2.0:WirelessText']), 'ALRT')
            else:
                self.sendAX("{}: {} - {}".format(alert['event'], alert['areaDesc'], alert['headline']), 'ALRT')

    def run(self):
        while True:
            time.sleep(0.2)
            item = self.p.getQueue()
            if item != False:
                counter = 0
                for q in item:
                    q['local-event'] = False
                    if self.p.filter_in_clc(q, self.cfg['naads']['zones']):
                        q['local-event'] = True
                    if self.p.filter_in_geo(q, self.geopoints):
                        q['local-event'] = True
                    if q['local-event'] == True:
                        logger.info("Local Event")
                        if q['language'] in self.cfg['naads']['language']:
                            self.sendAlerts(q)
                    self.elasticAdd(q)
                    counter += 1
                logger.info("Total events: {}".format(counter))
                self.elasticSend()

alert = Alerting()
alert.run()
