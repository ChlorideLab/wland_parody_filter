# -*- encoding: utf-8 -*-
# @File   : main.py
# @Time   : 2023/08/04 16:42:59
# @Author : Chloride

import asyncio
import logging

import yaml

import renderer
import wland
from regex_filter import filterPageRange

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s')

with open("./config.yaml", 'r', encoding="utf-8") as cfg:
    CONFIG: dict = yaml.load(cfg.read(), Loader=yaml.FullLoader)


if __name__ == '__main__':
    parody = wland.WlandParody(
        # positional settings
        CONFIG['domain'],
        CONFIG['parody'],
        # optional settings
        CONFIG.get('adult', False))  # def not to explicit R18

    results = filterPageRange(
        parody,
        CONFIG.get('start_page', 1),  # def from 1st to last
        CONFIG.get('end_page'),
        tag_forms=CONFIG.get('hashtags'),
        origin_forms=CONFIG.get('origins'),
        title_forms=CONFIG.get('title'),
        ignore_forms=CONFIG.get('ignores'))

    asyncio.run(renderer.outputHTML(CONFIG['domain'], *results))
    print("Done.")
