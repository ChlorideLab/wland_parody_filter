# -*- encoding: utf-8 -*-
# @File   : main.py
# @Time   : 2023/08/04 16:42:59
# @Author : Chloride

import logging

import yaml

import renderer
import wland
from regex_filter import filterPages

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

    results = filterPages(
        parody,
        CONFIG.get('start_page', 1),  # def from 1st to last
        CONFIG.get('end_page'),
        tags_match=CONFIG.get('hashtags'),
        origins_match=CONFIG.get('origins'),
        title_match=CONFIG.get('title'),
        negative_match=CONFIG.get('ignores'))

    renderer.outputHTML(CONFIG['domain'], *results)
    print("Done.")
