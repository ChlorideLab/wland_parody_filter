# -*- encoding: utf-8 -*-
# @File   : main.py
# @Time   : 2023/08/04 16:42:59
# @Author : Chloride

import asyncio
import logging

import yaml

import renderer
import wland
from regex_filter import filterPageRange, parseRegexes

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s')

with open("./config.yaml", 'r', encoding="utf-8") as cfg:
    CONFIG: dict = yaml.load(cfg.read(), Loader=yaml.FullLoader)

CONFIG['start_page'] = CONFIG.get('start_page', 1)
CONFIG['end_page'] = CONFIG.get('end_page')
CONFIG['ignores'] = parseRegexes(CONFIG.get('ignores'))
CONFIG['hashtags'] = parseRegexes(CONFIG.get('hashtags'))
CONFIG['origins'] = parseRegexes(CONFIG.get('origins'))
CONFIG['title'] = parseRegexes(CONFIG.get('title'))

if __name__ == '__main__':
    del cfg  # not used anymore.
    parody = wland.WlandParody(
        CONFIG['domain'],
        CONFIG['parody'],
        CONFIG.get('adult', False))  # def not to explicit R18
    asyncio.run(filterPageRange(
        parody, renderer.CSV('./wland.csv'), **CONFIG))
    print("Done.")
