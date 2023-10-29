# -*- encoding: utf-8 -*-
# @File   : regex_filter.py
# @Time   : 2023/08/18 20:26:18
# @Author : Chloride

from asyncio import sleep
import logging
from random import randint
from re import Pattern
from re import compile as regex
from typing import Sequence

import requests

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

    dst = tuple(dst)
    found = False
    for i in src:
        j = 0
        while j < len(dst) and (_ := i.search(dst[j])) is None:
            j += 1
        if found := _ is not None and (not fullstr or _.group() == dst[j]):
            break
    return found


class _CycleCache:  # to skip when contents updated.
    def __init__(self, capacity):
        self.__cache = [-114514] * capacity
        self.__max = capacity
        self.__cur = 0

    def store(self, elem):
        self.__cache[self.__cur] = elem
        self.__cur = (self.__cur + 1) % self.__max

    def exists(self, elem):
        return elem in self.__cache


def parseRegexes(seq) -> Sequence[Pattern]:
    if seq is None:
        seq = ()
    elif isinstance(seq, str):
        seq = [seq]

    for i in range(len(seq)):
        seq[i] = regex(seq[i])
    return seq


def filterContent(self: WlandPassage, **kw):
    merged = self.hashtags | {self.title}
    if self.tags:
        merged |= self.tags

    return (_inhibitor(kw['ignores'], merged) and
            (_finder(kw['hashtags'], self.tags) or
             _finder(kw['title'], [self.title], fullstr=False)) and
            _finder(kw['origins'], self.hashtags))


async def filterPageRange(self: WlandParody, file: SheetGenerator, **kw):
    """Filter through pages.

    Only passages with conditions below ALL satisfied will be collected:

    1. nobody matched one of "ignore".
    2. someone matched one of "title" OR "tag", respectively.
    3. one of the origin hashtags matched one of "origin".

    Those keywords with `None` value means we skip checking it.
    """
    start, end, total = kw['start_page'], kw['end_page'], self.num_pages
    if not 0 < start <= total:
        return
    if end is None or end < start or end > total:
        end = total
    await file.open()

    cache = _CycleCache(((end - start + 1) & 0xF) * 10)  # 10 - 150

    for cnt in range(start, end + 1):
        logging.info(f"Fetching page {cnt} / {end}")
        try:
            contents = self.fetchPagePassages(cnt)
        except requests.exceptions.RequestException as e:
            logging.critical(f"Abnormal network!\n\t{e}")
            break

        for c in contents:
            if cache.exists(c.wid):
                continue
            cache.store(c.wid)
            if not filterContent(c, **kw):
                continue
            logging.debug(str(c))
            if file.stream is not None:
                await file.append(c)
        await sleep(randint(2, 5))
    await file.close()
