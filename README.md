# wland_parody_filter
**【已弃用】** Wland 同人专区屏蔽/筛选文章的爬虫

## 注意事项

微软 Edge 浏览器新版本 `117.0.2045.31` 对 Cookies 的外部访问作了限制，
换言之，无法为 Edge 提供完整的专区筛选服务。  
出于对国产浏览器的不信任，我也无从得知 QQ 浏览器、360 浏览器之流是否也有相关限制。  
因此，本脚本现**仅对 Google Chrome** 提供可靠的爬取服务。

本仓库代码仅供学习交流用，**切勿用于恶意用途**。

> 竭泽而渔，岂不获得？而明年无鱼。

## Wland 文章条目
为便于后面解释，姑且放一张样图：

![Example](https://gitlab.com/ChlorideP/wland_parody_filter/raw/master/img/example.jpg)

- 标题 `Title`：虚线上方的加粗文本
- 作者 `Author`：如图所示
- 原型 `Origins`：图示左下角（# 块）  
由于同一个专区存在公共原型（如图为“崩坏三”），实际筛选/屏蔽时不考虑公共原型。
- 标签 `Tags`：图示正底部（🏷️ 块）

输出的文件可能还有作者`UID`和`WID`两列，详见[产出结果](#产出结果-wland)

## 抓取规则
仅当文章**同时满足**下列条件时，才能添加进筛选结果：
1. **所有**标签、**所有**原型、标题**均**未被`ignores`屏蔽；
2. 标题**或**标签符合`tags`要求。（顺序从左到右）
3. 原型符合`origins`要求。

上述`ignores` `tags` `origins`均为[正则表达式](https://gitlab.com/ChlorideP/wland_parody_filter/blob/master/README.REGEX.md)的集合。  
您也可以直接像查百度那样，直接把关键词罗列进配置文件。往下翻就知道怎么写了。

> 所谓「符合要求」，是指在目标范围内，找到**一条**符合限定规则**之一**的记录。  
> 比如匹配标签，就是在「这些标签当中」，找到「其中一条」符合「其中一个要求」的 Tag。

> 就我个人的发现，一般说的 Tag 更有可能出现在标签和标题；而原型更像是描述「相关人物」。  
> ~~当然，同人站点是自由的（~~

从配置文件中**删除**某一环节，或者**为某一环节置`null`**，则跳过该环节（认为符合要求/未被屏蔽）。

## 配置文件 `config.yaml`
假设你访问原神专区，浏览器地址栏显示`X.com/special/GenshinImpact`。  
请特别注意：
- Wland 域名并非真的是`X.com`，**需要手动替换**；  
  ~~（实际上这是推特或者说 X 的域名）~~
- 如需要筛选“成年”以上分级，需要**预先在 Chrome 浏览器里登上 Wland 账号**；  
  为什么非得是 Chrome？[因为别的浏览器不（清楚是否）允许](#注意事项)。

```yaml
parody: GenshinImpact   # 专区
domain: X.com   # wland 域名

# 下列选项均选填，不需要可以删除，并用如下默认值代替

start_page: 1   # 1 <= 起始页 <= 最后页 <= 最大页数
end_page: 2147483648  # 会自动改为分区实际页数（但往往不可能全部爬完）
adult: False    # 是否包含“成年”以上分级

# 下列选项均允许 直接删除、留空、只填一个、填入多个 四种处理。
# 直接删除与留空效果一致。

ignores: null   # 屏蔽正则（优先检查。留空示例）
tags:          # 标签、标题正则（次优先。填入多个示例）
  - '[孙行者][孙行者][孙行者]'
  # 由于中括号在 yaml 里有别的意义，不能直接起头
  # 故用单（双）引号包住表示字符串。
  - all[\u4e00-\u9fff]+
  - (原神|碧蓝档案|碧蓝航线)，启动！
origins: 芙宁娜    # 原型正则（只填一个示例）
```

### 关于代理
稳定性未知。可向`config.yaml`粘贴如下内容：
```yaml
proxy:
  https: "http://127.0.0.1:port"  # port 为你代理软件的端口号，自行百度
```

## 异常处理
- 还没开始爬就报错：请**先关闭所有浏览器**。
- 为确保 Wland 和您账号的可持续发展，爬取过程中的网络异常会被程序自行捕获，并及时中止爬取。
> 如您**使用了代理软件**却**未**在配置中[设置端口](#关于代理)，不妨**退出代理**重试。

## 产出结果 `wland.*`
默认是`wland.csv`，可以用 Excel 或记事本打开。
但 CSV 不适合插入链接，因此 WID 和 UID 均会直接给出。

除`CSV`外，`renderer.py`还提供了`.md`和`.html`文件的支持。  
MarkDown 更面向文档作者，HTML 则对读者更友好。二者均能通过链接跳转至对应的网页。

如需更改，可在`main.py`里将
```python
sheet_file = renderer.CSV('./wland.csv')
```
替换为其他格式：
```python
sheet_file = renderer.MarkDown('./wland.md', CONFIG['domain'])
```
```python
sheet_file = renderer.HTML('./wland.html', CONFIG['domain'])
```