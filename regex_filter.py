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


def _matching_xnor(src, dst, *, neglect=False):
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
                if (re.search(i, j) is None) ^ neglect:
                    law_kept = False
                    break
    finally:
        return law_kept


def _matching_or(src, dst, *, full_match=True):
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
        tags_match=None,
        origins_match=None,
        title_match=None,
        negative_match=None) -> list[WlandPassage] | tuple:
    """Filter logic (the following statements connected with `AND`):
    - `NO` string match negative regexes
    - Title `OR` Tag `AND` Origin strings match correlated regexes
    """

    ret, cache = list(), CycleCache(20)
    pages = parody.num_pages  # lessen the HTTP request
    if not 0 < page_start <= pages:
        return ()
    if page_end is None or page_end < page_start or page_end > pages:
        page_end = pages

    def filterContent(self: WlandPassage):
        merged = self.origins + (self.title,)
        if self.tags:
            merged += self.tags

        if (_matching_xnor(negative_match, merged, neglect=True) and
            (_matching_or(tags_match, self.tags) or
             _matching_or(title_match, [self.title], full_match=False) and
             _matching_or(origins_match, self.origins))):
            logging.debug(str(self))
            ret.append(self)

    for cnt in range(page_start, page_end + 1):
        logging.info(f"Fetching page {cnt} / {page_end}")
        try:
            contents = parody.getPageX(cnt)
        except requests.exceptions.RequestException as e:
            logging.critical(f"Abnormal network!\n\t{e}")
            break

        for c in contents:
            if cache.exists(c.wid):
                continue
            else:
                cache.store(c.wid)
                filterContent(c)
        sleep(randint(2, 5))
    return ret
