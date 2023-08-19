# -*- encoding: utf-8 -*-
# @File   : config.py
# @Time   : 2023/08/04 20:26:19
# @Author : Chloride

import yaml

with open("./config.yaml", 'r', encoding="utf-8") as cfg:
    config = yaml.load(cfg.read(), Loader=yaml.FullLoader)

PARODY = config["parody"]
DOMAIN = config["domain"]

HASHTAGS = config["hashtags"]
ORIGINS = config["origins"]
RELATIONS = config["relations"]

START_PAGE = config["start_page"]
if START_PAGE is None:
    START_PAGE = 1
END_PAGE = config["end_page"]
