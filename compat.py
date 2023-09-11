# -*- encoding: utf-8 -*-
# @File   : compat.py
# @Time   : 2023/09/11 14:37:38
# @Author : Chloride

# for Python < 3.9
def removeSuffix(self: str, suffix: str, /) -> str:
    if suffix and self.endswith(suffix):
        return self[:-len(suffix)]
    else:
        return self[:]
