#!/usr/bin/env python3

import colorlog
import logging
import yaml
from lib.pelmorex import Alerting

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
logger.addHandler(handler)

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

alert = Alerting(cfg)
alert.run()
