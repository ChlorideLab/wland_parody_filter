# wland_parody_filter
~~同人专区避雷工具~~ 检索特定CP、Tag并导出wid表  
问就是找炒饭不易——搜索只能找白米饭，专区里一页页翻既累又烦。。

## 注意事项

1. **搜索结果仅供参考。**
2. 在挂了代理的情况下，有可能发生如下 SSL 验证错误。
  **建议关闭加速器**重试。有更好的办法欢迎分享。

```log
[2023-08-14 16:12:26,406] CRITICAL: Abnormal network: HTTPSConnectionPool(host='...', port=443): Max retries exceeded with url: ... (Caused by SSLError(SSLEOFError(8, 'EOF occurred in violation of protocol (_ssl.c:1002)')))
```

3. **若发生任何可能的利益纠纷，还请优先维护 Wland 站方。**

> 竭泽而渔，岂不获得？而明年无鱼。


## 配置文件 `config.yaml`
```yaml
# 专区，即进入那个专区后url最后一个 / 后面的字符
parody: GenshinImpact
# wland 的域名
domain: 

# 1 <= 起始页 <= 最大页数
start_page: 1
# 起始页 < 最后页 <= 最大页数
end_page: 10

# 标签（正则表达式）
hashtags: null  # 不匹配，照单全收
hashtags: 水仙  # 有水仙就收
hashtags: # 下列限定中任何一个成立就算匹配
  - ^mob((?=[^钟海]).)*$  # 屏蔽 mob*钟* 或 mob*海*
  - c.?untboy  # 匹配 cuntboy countboy（真有这么写Tag的）

# 原型（正则表达式）
# 同样有三种写法，多个限定同样只需满足任意一个
origins: null

# 人物关系（正则表达式）
# 给定的人物关系（CP或登场人物）必须全部匹配
relations: null
```

## 产出结果 `wland.*`
默认是`wland.html`。~~浏览器总该人人都有吧？~~  
当然旧版的 Markdown 表示仍然保留（参见`renderer.py`）

由于个人觉得此脚本规模较小，没必要单独做本地化；并且表格的框架固定在源代码里，  
因此输出的结果有些许英文单词。翻译如下：

- `Search Result`  搜索结果
- `Author`  作者（允许点击以跳转到ta的主页）
- `Title`  文章标题（允许点击以阅览该文）
- `Origins`  原型，对应 Wland 文章条目的 # 部分。
- `Tags`  标签，对应 Wland 文章条目的 标签 部分。
