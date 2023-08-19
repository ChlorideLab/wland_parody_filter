# -*- encoding: utf-8 -*-
# @File   : regex_filter.py
# @Time   : 2023/08/18 20:26:18
# @Author : Chloride

import logging
import re
import time
from random import randint

import requests

from wland import WlandParody, WlandPassage


def _matching_and(src, dst):
    law_kept = True
    try:
        for i in src:
            if not law_kept:  # must be fully confirmed
                break
            for j in dst:
                match_ = re.search(i, j)
                if (not match_ or
                        (match_.group() != j and
                         match_.start() != 0 and
                         match_.end() != len(j))):
                    law_kept = False
                    break
    finally:
        return law_kept


def _matching_or(src, dst):
    skip_further_checking = False
    # I hate too much indentation
    try:
        for i in src:
            if skip_further_checking:
                break  # no need to match anymore
            for j in dst:
                match_ = re.search(i, j)
                if match_ and match_.group() == j:
                    skip_further_checking = True
                    break
    except TypeError:
        skip_further_checking = True
    return skip_further_checking


def filterPages(parody: WlandParody,
                page_start=1, page_end=-1, *,
                tags_match=None,
                origins_match=None,
                relations_match=None) -> list[WlandPassage] | tuple:
    ret = []

    pages = parody.num_pages  # lessen the HTTP request
    if not 0 < page_start <= pages:
        return ()
    if page_end is None or page_end < page_start or page_end > pages:
        page_end = pages

    if type(tags_match) is str:
        tags_match = [tags_match]
    if type(origins_match) is str:
        origins_match = [origins_match]
    if type(relations_match) is str:
        relations_match = [relations_match]

    for cnt in range(page_start, page_end + 1):
        logging.info(f"Page: {cnt} / {page_end}")
        try:
            contents = parody.getPageX(cnt)
        except requests.exceptions.RequestException as e:
            logging.critical(f"Abnormal network: {e}")
            break

        for p in contents:
            # logging.debug(str(p))
            if (_matching_and(relations_match, p.tags) and
                    _matching_and(relations_match, p.origins) and
                    _matching_and(relations_match, [p.title]) and
                    _matching_or(tags_match, p.tags) and
                    _matching_or(origins_match, p.origins)):
                ret.append(p)
        logging.debug(f"[Filter] {len(ret)} passages up to now.")
        time.sleep(randint(2, 5))
    return ret
