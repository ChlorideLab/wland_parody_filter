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
    config: dict = yaml.load(cfg.read(), Loader=yaml.FullLoader)
if config.get('start_page') is None:
    config['start_page'] = 1


if __name__ == '__main__':
    genshin = wland.WlandParody(
        # positional settings
        config['domain'], config['parody'], True)
    results = filterPages(
        genshin,
        config['start_page'],
        # optional settings
        config.get('end_page'),
        tags_match=config.get('hashtags'),
        origins_match=config.get('origins'),
        title_match=config.get('title'))

    renderer.outputHTML(config['domain'], *results)
    print("Done.")
