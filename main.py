# -*- encoding: utf-8 -*-
# @File   : main.py
# @Time   : 2023/08/04 16:42:59
# @Author : Chloride

import logging

import config
import wland
from regex_filter import filterPages

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s')


if __name__ == '__main__':
    genshin = wland.WlandParody(config.DOMAIN, config.PARODY, True)
    results = filterPages(
        genshin,
        config.START_PAGE,
        config.END_PAGE,
        tags_match=config.HASHTAGS,
        origins_match=config.ORIGINS,
        relations_match=config.RELATIONS)

    with open("./wland.md", 'w', encoding="utf-8") as fp:
        fp.write("|Author|Title|Origins|Tags|\n")
        fp.write("|-|-|-|-|\n")
        for i in results:
            fp.write("|%s|%s|%s|%s|\n" % (
                f"[{i.user_name}](https://{config.DOMAIN}/{i.uid})",
                f"[{i.title}](https://{config.DOMAIN}/wid{i.wid})",
                ",".join(i.origins),
                ",".join(i.tags) if i.tags is not None else ""
            ))
    print("Done.")
