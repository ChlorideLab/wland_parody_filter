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
    parody = wland.WlandParody(
        # positional settings
        config['domain'],
        config['parody'],
        config.get('adult', False))  # by default shouldn't allow R18.

    results = filterPages(
        parody,
        config['start_page'],
        # optional settings
        config.get('end_page'),
        tags_match=config.get('hashtags'),
        origins_match=config.get('origins'),
        title_match=config.get('title'),
        negative_match=config.get('ignores'))

    renderer.outputHTML(config['domain'], *results)
    print("Done.")
