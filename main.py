# -*- encoding: utf-8 -*-
# @File   : main.py
# @Time   : 2023/08/04 16:42:59
# @Author : Chloride

import asyncio
import logging

from globalvars import CONFIG
from regex_filter import filterPageRange
from renderer import initSheet
from wland import WlandParody

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s')

if __name__ == '__main__':
    parody = WlandParody(
        CONFIG['domain'],
        CONFIG['parody'],
        CONFIG.get('adult', False))  # def not to explicit R18
    sheet_file = initSheet(CONFIG.get('output', 'csv'), CONFIG['domain'])
    asyncio.run(filterPageRange(parody, sheet_file, **CONFIG))
    logging.info("Done.")
