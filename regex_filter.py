# -*- encoding: utf-8 -*-
# @File   : regex_filter.py
# @Time   : 2023/08/18 20:26:18
# @Author : Chloride

import logging
import re
import time

import requests

from wland import WlandParody


def _matching_xnor(src, dst, neglect=False):
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
                match_ = re.search(i, j)
                if not ((match_ is not None) ^ neglect):
                    law_kept = False
                    break
    finally:
        return law_kept


def _matching_or(src, dst):
    if type(src) is str:
        src = [src]

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
                title_match=None,
                negative_match=None):
    """Filter pages in range

    Get contents from `page_start` to `page_end`,
    and filter them page by page.

    Arguments:
        - `tags_match` `origins_match` `title_match`
            Regexes to MATCH
        - `negative_match`
            Regexes to IGNORE

    Returns:
        `list[WlandPassage]` if `page_start` is valid,
        otherwise an empty tuple `()`.
    """
    ret = []

    pages = parody.num_pages  # lessen the HTTP request
    if not 0 < page_start <= pages:
        return ()
    if page_end is None or page_end < page_start or page_end > pages:
        page_end = pages

    for cnt in range(page_start, page_end + 1):
        logging.info(f"Fetching page {cnt} / {page_end}")
        try:
            contents = parody.getPageX(cnt)
        except requests.exceptions.RequestException as e:
            logging.critical(f"Abnormal network!\n\t{e}")
            break

        for p in contents:
            # logging.debug(str(p))
            merged = p.origins + (p.title,)
            if p.tags:
                merged += p.tags

            if (_matching_xnor(negative_match, merged, neglect=True)
                    and _matching_xnor(title_match, [p.title])
                    and _matching_or(tags_match, p.tags)
                    and _matching_or(origins_match, p.origins)):
                logging.debug(str(p))
                ret.append(p)
        time.sleep(2)
    return ret
