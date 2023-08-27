# -*- encoding: utf-8 -*-
# @File   : main.py
# @Time   : 2023/08/04 16:42:59
# @Author : Chloride

import logging

import config
import renderer
import wland
from regex_filter import filterPages

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s')


if __name__ == '__main__':
    genshin = wland.WlandParody(config.DOMAIN, config.PARODY, True)
    results = filterPages(
        genshin,
        config.START_PAGE,
        config.END_PAGE,
        tags_match=config.HASHTAGS,
        origins_match=config.ORIGINS,
        relations_match=config.RELATIONS)

    renderer.outputHTML(config.DOMAIN, *results)
    print("Done.")
