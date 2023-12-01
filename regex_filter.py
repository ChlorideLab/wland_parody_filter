# -*- encoding: utf-8 -*-
# @File   : regex_filter.py
# @Time   : 2023/08/18 20:26:18
# @Author : Chloride

import asyncio
import logging
from random import random
from re import Pattern
from threading import Thread
from typing import List, Mapping, Optional, Sequence

from globalvars import REGEXES
from renderer import SheetGenerator
from wland import WlandParody, WlandPassage


def _inhibitor(src: Sequence[Pattern], dst):  # , *, neglect=False):
    if not src:
        return True

    dst = tuple(dst)
    confirmed = False
    for i in src:
        j = 0
        while j < len(dst) and i.search(dst[j]) is None:
            j += 1
        if not (confirmed := j == len(dst)):
            break
    return confirmed


def _finder(src: Sequence[Pattern], dst, *, fullstr=True):
    if not src:
        return True
    if not dst:
        return False  # should also assert title. see filterPassage()

    dst = tuple(dst)
    found = False
    for i in src:
        j = 0
        while j < len(dst) and (_ := i.search(dst[j])) is None:
            j += 1
        if found := _ is not None and (not fullstr or _.group() == dst[j]):
            break
    return found


class _PageCache:  # to skip when contents updated.
    def __init__(self, size=10):
        self.__lst: List[Optional[WlandPassage]] = [None] * size
        self._max = size
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


def filterPassage(self: WlandPassage,
                  regexes: Mapping[str, Sequence[Pattern]]):
    """Regex Assertion for specific WlandPassage

    To check whether given passage information can be picked,
    which in other words, must satisfy ALL the following conditions:

    1. NOBODY matched anyone of `regexes['ignores']`.
    2. AT LEAST ONE tag OR title matched one of `regexes['tags']`.
    3. one of the origin hashtags matched one of `regexes['origins']`.

    Those keywords with empty sequence (NOT `None`!) means we skip checking it.
    """
    merged = self.hashtags | self.tags | {self.title}
    return (_inhibitor(regexes['ignores'], merged)
            and (_finder(regexes['tags'], self.tags)
                 or _finder(regexes['tags'], [self.title], fullstr=False))
            and _finder(regexes['origins'], self.hashtags))


async def filterPageRange(self: WlandParody,
                          file: SheetGenerator,
                          **kwargs):
    """Filter through pages.

    C version condition expression:
        `!ignored && (a_tag_picked || title_picked) && an_origin_picked`\n
    See `help(filterPassage)` for detailed conditions.

    Arguments:
        - `self`: specific wland parody to fetch information
        - `file`: table file to output success results.

    Keyword Arguments:
        Should be able to just extract `globalvars.CONFIG`.

        - `start_page`: def to 1.
        - `end_page`: def to INT32_MAX (auto).
        - `ignores`: regexes (must be `Sequence[re.Pattern]`)
        to inhibit negative findings. def to `()`.
        - `origins` `tags`: regexes (must be `Sequence[Pattern]`)
        to search expect results. def to `()`.
    """
    start, end = kwargs['start_page'], kwargs['end_page']
    if not 0 < start <= end:  # basic skip
        return
    total = self.page_num if self.fetchPage(start) else -1
    if end > total:
        end = total

    await file.open()
    cache, thread = _PageCache(), None
    while (start <= end):
        logging.info(f"Processing page {start} / {end}")
        pagecur = self.getPage(start)
        if pagecur is None:
            logging.error("Failed even after retry. Stop filtering.")
            break
        if start != end:
            thread = Thread(target=self.fetchPage, args=(start + 1,))
            thread.daemon = True
            await asyncio.sleep(random() + 1)  # [1, 2) secs
            thread.start()
        for i in REGEXES['_mylist'].findall(pagecur.text):
            i = WlandPassage.parseHTML(i)
            if cache.find(i.wid):
                continue
            cache.store(i)
            if not filterPassage(i, kwargs):
                continue
            print(i)
            if file.stream is not None:
                await file.append(i)
        if thread is not None:
            thread.join()  # must be finished when next page coming
        start += 1
    await file.close()
