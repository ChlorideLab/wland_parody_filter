# -*- encoding: utf-8 -*-
# @File   : wland.py
# @Time   : 2023/08/04 12:50:13
# @Author : Chloride

import logging
from typing import AnyStr
from typing import NamedTuple as Struct
from typing import Optional, Set

import browser_cookie3 as cookies
import requests

from globalvars import HEADER, PROXY, REGEXES


class WlandPassage(Struct):
    wid: int
    title: str
    author_uid: int
    author_name: str
    hashtags: Set[str]  # should NOT be empty
    tags: Set[str]  # MAY BE EMPTY

    def __str__(self) -> str:
        title = "{:15.15}".format(self.title)
        if self.title not in title:
            title += '...'
        return "wid{0: <8}  {1} by {2} (u{3})".format(
                self.wid, title, self.author_name, self.author_uid)

    @classmethod
    def parseHTML(cls, dl_mylist: AnyStr):
        wid = int(REGEXES['wid'].search(dl_mylist).group().replace('wid', ''))
        title = REGEXES['title'].search(dl_mylist).group()
        if not (title := REGEXES['HTML'].sub('', title)):
            title = "NO TITLE"
        author = REGEXES['author'].search(dl_mylist).group()
        category = REGEXES['category'].findall(dl_mylist)
        return cls(wid, title, **{
            'author_uid': int(REGEXES['INT'].search(author).group()),
            'author_name': REGEXES['HTML'].sub('', author),
            'hashtags': set(REGEXES['TAG'].sub('', category[0])
                            .replace('</span>', '')
                            .split(' , ')),
            'tags': set(REGEXES['TAG'].sub('', category[1])
                        .replace('</span>', '')
                        .split(' , ')) if len(category) > 1 else set()})


class WlandParody:
    def __init__(self, url=None, parody=None, adult=False):
        """You have to sign in before scanning.
        The user information will be automatically collected."""
        self.url = f'{url}/special/{parody}'
        self.cookie = cookies.chrome(domain_name=url) if adult else None
        self._session = requests.Session()
        self._session.headers.update(HEADER)
        self._session.proxies = PROXY
        self._page_cur = -1
        self._fetched: Optional[requests.Response] = None

    def __repr__(self):
        return self.url

    @property
    def page_num(self):
        if not self._fetched or self._fetched.status_code != 200:
            self.fetchPage()
        return int(REGEXES['_pages'].search(self._fetched.text).group()[3:-1])

    def getPage(self, page):
        if page != self._page_cur or self._fetched.status_code != 200:
            self.fetchPage(page)
        return self._fetched

    def fetchPage(self, page=1):
        try:
            self._fetched = self._session.get(
                f"https://{self.url}/page={page}", cookies=self.cookie)
            self._page_cur = page
        except requests.RequestException as e:
            logging.warning(f"Failed to fetch p{page}: {e.__class__.__name__}")
            print(f"Details: \n\t{e.args}")
            self._fetched = None
            self._page_cur = -1
        return self._fetched is not None and self._fetched.status_code == 200
