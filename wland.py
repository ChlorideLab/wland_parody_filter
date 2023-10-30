# -*- encoding: utf-8 -*-
# @File   : wland.py
# @Time   : 2023/08/04 12:50:13
# @Author : Chloride

from typing import AnyStr, List
from typing import NamedTuple as Struct
from typing import Optional, Set

import browser_cookie3 as cookies
import requests

from globalvars import REGEXES, HTTP_HEADER


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
        self._max = capacity
        self._cur = 0

    def store(self, elem):
        self.__lst[self._cur] = elem
        self._cur = (self._cur + 1) % self._max

    def find(self, wid: int):
        i, j = self._cur, 0
        while (j < self._max and self.__lst[i] and self.__lst[i].wid != wid):
            i = (i + 1) % self._max
            j += 1
        self._cur = (i if (j := j == self._max or not self.__lst[i])
                     else i + 1) % self._max
        return not j

    def toTuple(self):
        return tuple(self.__lst)


class WlandParody:
    def __init__(self, url=None, parody=None, adult=False):
        """You have to sign in before scanning.
        The user information will be automatically collected."""
        self.url = f'{url}/special/{parody}'
        self.cookie = cookies.chrome(domain_name=url) if adult else None
        self._cache = _CycleCache(10)
        self._page_cached = 0
        self._page_total = 0

    def __repr__(self):
        return self.url

    @property
    def page_num(self):
        if not self._page_total:
            self.fetchPage()
        return self._page_total

    def fetchPage(self, page=1):
        if self._page_cached != page:
            response = requests.get(f"https://{self.url}/page={page}",
                                    cookies=self.cookie, headers=HTTP_HEADER)
            if response.status_code != 200:
                return ()
            self._page_total = int(
                REGEXES['_pages'].search(response.text).group()[3:-1])
            self._page_cached = page
            for i in REGEXES['_mylist'].findall(response.text):
                self._parse(i)
        return self._cache.toTuple()

    def _parse(self, dl_mylist: AnyStr):
        wid = int(REGEXES['wid'].search(dl_mylist).group().replace('wid', ''))
        if self._cache.find(wid):
            return
        title = REGEXES['title'].search(dl_mylist).group()
        if not (title := REGEXES['HTML'].sub('', title)):
            title = "NO TITLE"
        author = REGEXES['author'].search(dl_mylist).group()
        category = REGEXES['category'].findall(dl_mylist)
        self._cache.store(WlandPassage(wid, title, **{
            'author_uid': int(REGEXES['INT'].search(author).group()),
            'author_name': REGEXES['HTML'].sub('', author),
            'hashtags': set(REGEXES['TAG'].sub('', category[0])
                            .replace('</span>', '')
                            .split(' , ')),
            'tags': set(REGEXES['TAG'].sub('', category[1])
                        .replace('</span>', '')
                        .split(' , ')) if len(category) > 1 else set()}))
