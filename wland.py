# -*- encoding: utf-8 -*-
# @File   : wland.py
# @Time   : 2023/08/04 12:50:13
# @Author : Chloride

from re import S as FULL_MATCH
from re import compile as regex
from typing import AnyStr, List
from typing import NamedTuple as Struct
from typing import Optional, Set

import browser_cookie3 as cookies
import requests

_REGEXES = {
    # parse
    '_pages': regex(r">\.\.[0-9]+<"),
    '_mylist': regex(
        r'<dl class="MyList" id="[a-z0-9_]+">.*?</dl>',
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


class WlandPassage(Struct):
    wid: int
    title: str
    author_uid: int
    author_name: str
    hashtags: Set[str]  # should NOT be empty
    tags: Set[str]  # MAY BE EMPTY


class _CycleCache:  # to skip when contents updated.
    def __init__(self, capacity):
        self.__lst: List[Optional[WlandPassage]] = [None] * capacity
        self.__max = capacity
        self.__cur = 0

    def store(self, elem):
        self.__lst[self.__cur] = elem
        self.__cur = (self.__cur + 1) % self.__max

    def next(self):
        self.__cur = (self.__cur + 1) % self.__max

    def find(self, wid: int):
        i = 0
        while (i < self.__max):
            if self.__lst[i] is None or self.__lst[i].wid == wid:
                break
            i += 1
        return i < self.__max and self.__lst[i] is not None

    def toTuple(self):
        return tuple(self.__lst)


class WlandParody:
    def __init__(self, url=None, parody=None, adult=False):
        """You have to sign in before scanning.
        The user information will be automatically collected."""
        self.url = url
        self.parody = parody
        self.cookie = cookies.chrome(domain_name=url) if adult else None
        self._cache = _CycleCache(10)
        self._page_cached = 0
        self._page_total = 0

    def __repr__(self):
        return f'{self.url}/special/{self.parody}'

    @property
    def page_num(self):
        if not self._page_total:
            self.fetchPage()
        return self._page_total

    def fetchPage(self, page=1):
        if self._page_cached != page:
            fetched = requests.get(
                f"https://{self.url}/special/{self.parody}/page={page}",
                cookies=self.cookie)
            if fetched.status_code != 200:
                return ()
            self._page_total = int(
                _REGEXES['_pages'].search(fetched.text).group()[3:-1])
            self._page_cached = page
            for i in _REGEXES['_mylist'].findall(fetched.text):
                self._parse(i)
        return self._cache.toTuple()

    def _parse(self, dl_mylist: AnyStr):
        wid = int(_REGEXES['wid'].search(dl_mylist).group().replace('wid', ''))
        if self._cache.find(wid):
            self._cache.next()
            return
        title = _REGEXES['title'].search(dl_mylist).group()
        if not (title := _REGEXES['HTML'].sub('', title)):
            title = "NO TITLE"
        author = _REGEXES['author'].search(dl_mylist).group()
        category = _REGEXES['category'].findall(dl_mylist)
        self._cache.store(WlandPassage(wid, title, **{
            'author_uid': int(_REGEXES['INT'].search(author).group()),
            'author_name': _REGEXES['HTML'].sub('', author),
            'hashtags': set(_REGEXES['TAG'].sub('', category[0])
                            .replace('</span>', '')
                            .split(' , ')),
            'tags': set(_REGEXES['TAG'].sub('', category[1])
                        .replace('</span>', '')
                        .split(' , ')) if len(category) > 1 else set()}))
