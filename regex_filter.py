# -*- encoding: utf-8 -*-
# @File   : regex_filter.py
# @Time   : 2023/08/18 20:26:18
# @Author : Chloride

import logging
import re
from random import randint
from time import sleep

import requests

from wland import WlandParody


def _inhibitor(src, dst):  # , *, neglect=False):
    """XNOR logic filter

    Only in these following situations returns `True`:
    - `All` keys matched && `neglect=False`
    - `No` keys matched && `neglect=True`

    Otherwise returns `False`.
    """
    if type(src) is str:
        src = [src]

    law_kept = True
    try:
        for i in src:
            if not law_kept:  # must be fully confirmed
                break
            for j in dst:
                # if (re.search(i, j) is None) ^ neglect:
                if re.search(i, j) is not None:
                    law_kept = False
                    break
    finally:
        return law_kept


def _finder(src, dst, *, full_match=True):
    if type(src) is str:
        src = [src]

    skip_check = False
    # I hate too much indentation
    try:
        for i in src:
            if skip_check:
                break  # no need to match anymore
            for j in dst:
                if (match_ := re.search(i, j)):
                    skip_check = not full_match or match_.group() == j
                    break
    except TypeError:
        skip_check = True
    return skip_check


class CycleCache:  # to skip when contents updated.
    def __init__(self, capacity):
        self.__cache = [-114514] * capacity
        self.__max = capacity
        self.__cur = 0

    def store(self, elem):
        self.__cache[self.__cur] = elem
        self.__cur = (self.__cur + 1) % self.__max

    def exists(self, elem):
        return elem in self.__cache


def filterPageRange(
        parody: WlandParody, page_start=1, page_end=-1, *,
        tag_forms=None,
        origin_forms=None,
        title_forms=None,
        ignore_forms=None) -> list[WlandPassage] | tuple:
    """Filter logic (the following statements connected with `AND`):
    - `NO` string matches negative regexes
    - Title `OR` Tag `AND` Origin strings match correlated regexes
    """
    pages = parody.num_pages  # lessen the HTTP request
    if not 0 < page_start <= pages:
        return ()
    if page_end is None or page_end < page_start or page_end > pages:
        page_end = pages

    ret, cache = list(), CycleCache(page_end - page_start)

    def filterContent(self: WlandPassage):
        merged = self.hashtags | {self.title}
        if self.tags:
            merged |= self.tags

        if (_inhibitor(ignore_forms, merged)
            and (_finder(tag_forms, self.tags)
                 or _finder(title_forms, [self.title], full_match=False)
                 and _finder(origin_forms, self.hashtags))):
            logging.debug(str(self))
            ret.append(self)

    for cnt in range(page_start, page_end + 1):
        logging.info(f"Fetching page {cnt} / {page_end}")
        try:
            contents = parody.fetchPagePassages(cnt)
        except requests.exceptions.RequestException as e:
            logging.critical(f"Abnormal network!\n\t{e}")
            break

        for c in contents:
            if cache.exists(c.wid):
                continue
            cache.store(c.wid)
            filterContent(c)
        sleep(randint(2, 5))
    return ret
