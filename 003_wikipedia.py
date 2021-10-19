# 爬取 wikipedia 搜索结果，并规整层级（代码很烂）

import requests
from lxml import etree


input_name = "尿毒症"

url = "https://zh.wikipedia.org/zh-hans/{}".format(input_name)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
}

response = requests.get(url, headers=headers)

html = etree.HTML(response.text)

mw_content_text = html.xpath('//*[@id="mw-content-text"]')

# 获取内容的所有标签并过滤掉 table 和 div 
contents = filter(lambda a: a.tag not in ["div", "table", "style"], mw_content_text[0].xpath("div[1]/*"))
result = []
current_h2 = None
current_h3 = None
for i, c in enumerate(contents):
    """
    层级关系
    1. p/ol/ul/h2
    2. h2 -> p/ol/ul/h3
    3. h3 -> p/ol/ul
    """
    if c.tag == 'h2':
        h2 = c.xpath("./span[@class='mw-headline']/text()")[0]
        if h2 in ["参考文献", "参见", "参考资料", "延伸阅读", "外部链接", "相关条目", "相关参看", "注释和参考资料"]:
            break
        result.append({h2: []})
        current_h2 = h2
        current_h3 = None

    if c.tag == "h3":
        h3 = c.xpath("./span[@class='mw-headline']/text()")[0]
        current_h3 = h3
        result[-1][current_h2].append({h3: []})

    if c.tag == "ul" or c.tag == "ol":
        li = c.xpath("./li")
        li_result = []
        for l in li:
            li_result.append("".join(l.xpath(".//text()")))

        if current_h2:
            if current_h3:
                result[-1][current_h2][-1][current_h3].append(li_result)
            else:
                result[-1][current_h2].append(li_result)
        else:
            result.append(li_result)

    if c.tag == "dl":
        li = c.xpath("./dd")
        li_result = []
        for l in li:
            li_result.append("".join(l.xpath(".//text()")))

        if current_h2:
            if current_h3:
                result[-1][current_h2][-1][current_h3].append(li_result)
            else:
                result[-1][current_h2].append(li_result)
        else:
            result.append(li_result)

    if c.tag == "p":
        p_content = "".join(c.xpath(".//text()")).strip()
        # 判断关系，如果此时h3和h2不为空
        if current_h2:
            if current_h3:
                result[-1][current_h2][-1][current_h3].append(p_content)
            else:
                result[-1][current_h2].append(p_content)
        else:
            result.append(p_content)

print(result)

response.close()
