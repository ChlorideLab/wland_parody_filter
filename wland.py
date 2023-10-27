# -*- encoding: utf-8 -*-
# @File   : wland.py
# @Time   : 2023/08/04 12:50:13
# @Author : Chloride

from re import M as MULTI_LINE
from re import compile as regex
from re import findall, search
from typing import List
from typing import NamedTuple as Struct
from typing import Set

import browser_cookie3 as cookies
import requests

_REGEXES = {
    # parse
    'wid': regex(r'wid[0-9]+'),
    'title': regex(r'<b>.*</b>'),
    'author': regex(r'<a href=".*u[0-9]+">.+</a>'),
    'filters': regex(r'<span class="CblockRevise Rtype5">.+?</span>'),
    # export
    'INT': regex(r'[0-9]+'),
    'HTML': regex(r'<.+?>'),
    'TAG': regex(r'.+</i> ')
}


class WlandPassage(Struct):
    wid: int
    title: str
    author_uid: int
    author_name: str
    hashtags: Set[str]  # should NOT be empty
    tags: Set[str]  # MAY BE EMPTY

    @classmethod
    def parseHTML(cls, raw_html):
        wid = _REGEXES['wid'].search(raw_html).group()
        title = _REGEXES['title'].search(raw_html).group()
        author = _REGEXES['author'].search(raw_html).group()
        filters = _REGEXES['filters'].findall(raw_html)
        return cls(**{
            'wid': int(_REGEXES['INT'].search(wid).group()),
            'title': ("NO TITLE"
                      if not (_ := _REGEXES['HTML'].sub('', title))
                      else _),
            'author_uid': int(_REGEXES['INT'].search(author).group()),
            'author_name': _REGEXES['HTML'].sub('', author),
            'hashtags': set(_REGEXES['TAG'].sub('', filters[0])
                            .replace('</span>', '')
                            .split(' , ')),
            'tags': set(_REGEXES['TAG'].sub('', filters[1])
                        .replace('</span>', '')
                        .split(' , ')) if len(filters) > 1 else set()})


class WlandParody:
    def __init__(self, url=None, parody=None, adult=False):
        """You have to sign in before scanning.
        The user information will be automatically collected."""
        self.url = url
        self.parody = parody
        # MSEdge has banned cookies access
        self.cookie = cookies.chrome(domain_name=url)
        self.adult_content = adult

    def __repr__(self):
        return f'{self.url}/special/{self.parody}'

    @property
    def num_pages(self):
        root = requests.get(
            f"https://{self.url}/special/{self.parody}",
            cookies=(self.cookie if self.adult_content else None))
        pages = search(r">\.\.[0-9]+<", root.text).group()
        return int(pages[3:-1])  # ignore signs

    def fetchPagePassages(self, page=1) -> List[WlandPassage]:
        ret = []

        page_on_server = requests.get(
            f"https://{self.url}/special/{self.parody}/page={page}",
            cookies=(self.cookie if self.adult_content else None)
        )
        if page_on_server.status_code == 200:
            # pages without any process should also be closed.
            # so we just do it in the block.
            items = findall(r'^<dl class="MyList".*>',
                            page_on_server.text, MULTI_LINE)
            for j in items:
                j = page_on_server.text[page_on_server.text.index(j):]
                ret.append(WlandPassage.parseHTML(j[:j.index("</dl>")]))

        return ret
