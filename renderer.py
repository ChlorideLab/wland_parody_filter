# -*- encoding: utf-8 -*-
# @File   : renderer.py
# @Time   : 2023/08/27 10:38:32
# @Author : Chloride

import aiofiles

from wland import WlandPassage


MD_TABLE_FRAMEWORK = """
|Author|Title|Origins|Tags|
|-|-|-|-|"""
MD_TABLE_ITEM = """|{0}|{1}|{2}|{3}|"""


async def outputMarkdown(domain, *wps: WlandPassage):
    async with aiofiles.open("./wland.md", 'w', encoding="utf-8") as fp:
        await fp.write(f"{MD_TABLE_FRAMEWORK}\n")
        for i in wps:
            await fp.write("%s\n" % MD_TABLE_ITEM.format(
                f"[{i.author_name}](https://{domain}/u{i.author_uid})",
                f"[{i.title}](https://{domain}/wid{i.wid})",
                ", ".join(i.hashtags),
                ", ".join(i.tags) if i.tags else ""))


HTML_HEAD = """
<html><head>
<meta charset="utf-8">
<title>Wland Parody Filter</title>
</head><body>"""

HTML_TABLE_FRAMEWORK = """<table border="1"><caption/>Search Result
<tr><th/>Author<th/>Title<th/>Origins<th/>Tags</tr>"""

HTML_TABLE_ITEM = """<tr><td/>{0}<td/>{1}<td/>{2}<td/>{3}</tr>"""

HTML_LINK = """\
<a href="{0}" target="_blank" rel="noopener noreferrer">{1}</a>"""

HTML_TAIL = """</table></body></html>"""


async def outputHTML(domain, *wps: WlandPassage):
    async with aiofiles.open("./wland.html", 'w', encoding="utf-8") as fp:
        await fp.write(f"{HTML_HEAD}\n")
        await fp.write(f"{HTML_TABLE_FRAMEWORK}\n")
        for i in wps:
            await fp.write("%s\n" % HTML_TABLE_ITEM.format(
                HTML_LINK.format(f"https://{domain}/u{i.author_uid}",
                                 i.author_name),
                HTML_LINK.format(f"https://{domain}/wid{i.wid}",
                                 i.title),
                ", ".join(i.hashtags),
                ", ".join(i.tags) if i.tags else ""))
        await fp.write(f"{HTML_TAIL}\n")
