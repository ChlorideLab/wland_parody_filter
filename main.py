# -*- encoding: utf-8 -*-
# @File   : main.py
# @Time   : 2023/08/04 16:42:59
# @Author : Chloride

import asyncio
import logging

import renderer
import wland
from globalvars import CONFIG
from regex_filter import filterPageRange

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s')

if __name__ == '__main__':
    parody = wland.WlandParody(
        CONFIG['domain'],
        CONFIG['parody'],
        CONFIG.get('adult', False))  # def not to explicit R18
    sheet_file = renderer.CSV('./wland.csv')
    asyncio.run(filterPageRange(parody, sheet_file, **CONFIG))
    print("Done.")
