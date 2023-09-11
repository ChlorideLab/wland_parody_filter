# -*- encoding: utf-8 -*-
# @File   : wland.py
# @Time   : 2023/08/04 12:50:13
# @Author : Chloride

import re
from dataclasses import dataclass
from typing import TypeAlias, TypeVar

import browser_cookie3 as cookies
import requests

from compat import removeSuffix

StrTuple: TypeAlias = "tuple[str]"
AnyStrTuple = TypeVar('AnyStrTuple', StrTuple, None)


@dataclass
class WlandPassage:
    wid: str
    title: str
    uid: str
    user_name: str
    tags: AnyStrTuple  # may have no tags
    origins: StrTuple


def recordContent(raw_html):
    wid = re.search(r"wid[0-9]+", raw_html).group()
    title = re.search(r"<b>.*</b>", raw_html).group()
    user = re.search(r'"u[0-9]+".*</a>', raw_html).group()

    # " str ", " str<"
    origins = tuple(
        removeSuffix(j, '<').strip()
        for j in re.findall(r' [A-Za-z0-9\u4E00-\u9FA5]+[ <]',
                            re.search(r"hashtag.*</?[ds]", raw_html)
                            .group()
                            .split('</span>')[0]))
    tags = re.search(r'tags.*</s', raw_html)
    if tags is not None:
        tags = tuple(
            removeSuffix(j, '<').strip()
            for j in re.findall(r' [A-Za-z0-9\u4E00-\u9FA5]+[ <]',
                                tags.group()))

    return WlandPassage(
        wid[3:],  # only keep digits
        re.sub(r"</?b>", "", title),  # rm html bold
        user[1: user[1:].index('"')],  # uid
        user[user.index('>') + 1: user.index('<')],  # user name
        tags,
        origins)


class WlandParody:
    def __init__(self, url=None, parody=None, adult=False):
        """You have to sign in before scanning.
        The user information will be automatically collected."""
        self.url = url
        self.parody = parody
        # unknown which browser
        self.cookie = cookies.load(url)
        self.adult_content = adult

    def __repr__(self):
        return f'special/{self.parody}'

    @property
    def num_pages(self):
        root = requests.get(
            f"https://{self.url}/special/{self.parody}",
            cookies=(self.cookie if self.adult_content else None))
        pages = re.search(r">\.\.[0-9]+<", root.text).group()
        return int(pages[3:-1])  # ignore signs

    def getPageX(self, page=1):
        """Get specific page contents.

        Returns:
            `list[WlandPassage]`
        """
        ret = []

        page_on_server = requests.get(
            f"https://{self.url}/special/{self.parody}/page={page}",
            cookies=(self.cookie if self.adult_content else None)
        )
        if page_on_server.status_code == 200:
            # pages without any process should also be closed.
            # so we just do it in the block.
            items = re.findall(r'^<dl class="MyList".*>',
                               page_on_server.text, re.M)
            for j in items:
                j = page_on_server.text[page_on_server.text.index(j):]
                ret.append(recordContent(j[:j.index("</dl>")]))

        return ret
