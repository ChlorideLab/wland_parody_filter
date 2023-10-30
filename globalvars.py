# -*- encoding: utf-8 -*-
# @File   : globalvars.py
# @Time   : 2023/10/30 22:27:40
# @Author : Chloride

from re import S as FULL_MATCH
from re import compile as regex

import yaml

from regex_filter import parseRegexes


with open("./config.yaml", 'r', encoding="utf-8") as cfg:
    CONFIG: dict = yaml.load(cfg.read(), Loader=yaml.FullLoader)

del cfg

CONFIG['start_page'] = CONFIG.get('start_page', 1)
CONFIG['end_page'] = CONFIG.get('end_page')
CONFIG['ignores'] = parseRegexes(CONFIG.get('ignores'))
CONFIG['hashtags'] = parseRegexes(CONFIG.get('hashtags'))
CONFIG['origins'] = parseRegexes(CONFIG.get('origins'))
CONFIG['title'] = parseRegexes(CONFIG.get('title'))

REGEXES = {
    # parse
    '_pages': regex(r">\.\.[0-9]+<"),
    '_mylist': regex(r'<dl class="MyList" id="[a-z0-9_]+">.*?</dl>',
                     FULL_MATCH),
    'wid': regex(r'wid[0-9]+'),
    'title': regex(r'<b>.*</b>'),
    'author': regex(r'<a href=".*u[0-9]+">.+</a>'),
    'category': regex(r'<span class="CblockRevise Rtype5">.+?</span>'),
    # export
    'INT': regex(r'[0-9]+'),
    'HTML': regex(r'<.+?>'),
    'TAG': regex(r'.+</i> ')
}


HTTP_HEADER = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/118.0.0.0 Safari/537.36"
}
