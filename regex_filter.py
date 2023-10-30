# -*- encoding: utf-8 -*-
# @File   : regex_filter.py
# @Time   : 2023/08/18 20:26:18
# @Author : Chloride

import asyncio
import logging
from random import randint
from re import Pattern
from typing import Mapping, Sequence

import requests

from renderer import SheetGenerator
from wland import WlandParody, WlandPassage, _CycleCache


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
    _ = None  # dst could be empty (tags).
    for i in src:
        j = 0
        while j < len(dst) and (_ := i.search(dst[j])) is None:
            j += 1
        if found := _ is not None and (not fullstr or _.group() == dst[j]):
            break
    return found


def filterPassage(self: WlandPassage,
                  regexes: Mapping[str, Sequence[Pattern]]):
    """Regex Assertion for specific WlandPassage

    To check whether given passage information can be picked,
    which in other words, must satisfy ALL the following conditions:

    1. NOBODY matched anyone of `regexes['ignores']`.
    2. AT LEAST ONE matched one of `regexes['title']`
    OR `regexes['hashtags']`, respectively.
    3. one of the origin hashtags matched one of `regexes['origins']`.

    Those keywords with empty sequence (NOT `None`!) means we skip checking it.
    """
    merged = self.hashtags | {self.title}
    if self.tags:
        merged |= self.tags

    return (_inhibitor(regexes['ignores'], merged)
            and (_finder(regexes['hashtags'], self.tags)
                 or _finder(regexes['title'], [self.title], fullstr=False))
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
        Should be able to just extract `main.CONFIG`.

        - `start_page`: def to 1.
        - `end_page`: def to `None` (auto).
        - `ignores`: regexes (must be `Sequence[re.Pattern]`)
        to inhibit negative findings. def to `()`.
        - `title` `origins` `hashtags`: regexes (must be `Sequence[Pattern]`)
        to search expect results. def to `()`.
    """
    start, end, total = kwargs['start_page'], kwargs['end_page'], self.page_num
    if not 0 < start <= total:
        return
    if end is None or end < start or end > total:
        end = total
    cache = _CycleCache((end - start + 1 & 0xF) * 10)  # 10-150.

    await file.open()
    for cnt in range(start, end + 1):
        logging.info(f"Fetching page {cnt} / {end}")
        try:
            contents = self.fetchPage(cnt)
        except requests.exceptions.RequestException as e:
            logging.critical(f"Abnormal network!\n\t{e}")
            break

        for c in contents:
            if cache.find(c.wid):
                continue
            cache.store(c)
            if not filterPassage(c, kwargs):
                continue
            logging.debug(f"Pick {c}")
            if file.stream is not None:
                await file.append(c)
        await asyncio.sleep(randint(1, 3))
    await file.close()
