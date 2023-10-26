# wland_parody_filter
**【已弃用】** Wland 同人专区屏蔽/筛选文章的爬虫

## 注意事项

微软 Edge 浏览器新版本 `117.0.2045.31` 对 Cookies 的外部访问作了限制，  
本脚本现**仅对 Google Chrome** 提供可靠的爬取服务。

本仓库代码仅供学习交流用，**切勿用于恶意用途**。还请优先维护 Wland 站方的利益。

> 竭泽而渔，岂不获得？而明年无鱼。

## 抓取规则
仅当文章**同时满足**下列条件时，才能添加进筛选结果：
1. 所有标签、所有原型、标题均未被屏蔽；
2. 标题 或 标签符合对应要求；
3. 原型符合对应要求。

从配置文件中**删除**某一环节，或者**为某一环节置`null`**，则跳过该环节（认为符合要求/未被屏蔽）。

## 配置文件 `config.yaml`
假设访问原神专区，浏览器地址栏为`X.com/special/GenshinImpact`。
```yaml
parody: GenshinImpact   # 专区
domain: X.com   # wland 域名 !! 需要替换为能用的真正域名 !!

# 下列选项均选填，不需要可以删除
# 全部删除后相当于没登 Wland 账号，进专区从第一页爬到最后一页，照单全收。

start_page: 1   # 1 <= 起始页 <= 最大页数
end_page: 10    # 起始页 < 最后页 <= 最大页数

adult: False    # 是否过滤成人向内容（若是，则需要浏览器先登上账号）

# 下列选项均允许三种写法。示例仅供参考（

# 屏蔽正则（优先检查）
ignores: null   # 留空 - 照单全收
# 标签正则
hashtags: .+ks  # ssks @2f打ks ... √ ks123 ×
# 原型正则
origins: null
# 标题正则
title:
  - '[孙行者][孙行者][孙行者]'
  # 孙行者 行者孙 者行孙 ……
  # 由于中括号在 yaml 里有别的意义，不能直接起头，故用单（双）引号包住表示字符串。
  - all[\u4e00-\u9fff]+
  # 上述范围内的常见中文字应该够我们用了。+ 则表示前面的 单字 可以出现一次或多次。
  # all千人律者 √（大雾）
  - (原神|碧蓝档案|碧蓝航线)，启动！
  # 原神，启动！... 在 () 范围内命中一个就匹配。| 是“或”的意思。
```

## 异常处理
- 还没开始爬就报错：请**先关闭所有浏览器**。
- 在挂了代理的情况下，有可能出现以下错误：**建议关闭加速器**重试。有更好的办法欢迎分享。

```log
[2023-08-14 16:12:26,406] CRITICAL: Abnormal network!
  HTTPSConnectionPool(host='...', port=443): Max retries exceeded with url: ... (Caused by SSLError(SSLEOFError(8, 'EOF occurred in violation of protocol (_ssl.c:1002)')))
[2023-09-15 00:09:40,399] CRITICAL: Abnormal network!
  ('Connection aborted.', ConnectionResetError(10054, '远程主机强迫关闭了一个现有的连接。', None, 10054, None))
```

## 产出结果 `wland.*`
默认是`wland.html`。~~浏览器总该人人都有吧？~~  
当然旧版的 Markdown 表示仍然保留（参见`renderer.py`）

- `Search Result`  搜索结果
- `Author`  作者（允许点击以跳转到ta的主页）
- `Title`  文章标题（允许点击以阅览该文）
- `Origins`  原型，对应 Wland 文章条目的 # 部分。
- `Tags`  标签，对应 Wland 文章条目的 标签 部分。
