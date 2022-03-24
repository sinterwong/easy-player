import requests
from lxml import etree
import pandas as pd
import numpy as np


medicine_infos = []

for i in range(1, 107):
    if i == 1:
        url = "https://www.zyctd.com/jiage/1-0-0.html"
    else:
        url = "https://www.zyctd.com/jiage/1-0-0-{}.html".format(i)

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    html = etree.HTML(response.text)

    ul = html.xpath('//*[@id="body"]/section/div/div[3]/div[1]/div[3]/div/ul')

    li = ul[0].xpath("./li")

    for l in li:
        medicine = l.xpath("./span[1]/a/text()")
        specification = l.xpath("./span[2]/a/text()")
        market = l.xpath("./span[3]/text()")
        price = l.xpath("./span[4]/text()")

        medicine_infos.append((medicine[0], specification[0], market[0], float(price[0])))

data_array = np.array(medicine_infos)
df = pd.DataFrame(data_array, columns=["medicine", "specification", "market", "price"])

df.to_excel('medicine_info.xlsx', index=False, header=True)

medicine2price = {}
for medicine, _, _, price in medicine_infos:
    medicine2price.setdefault(medicine, [])
    medicine2price[medicine].append(price)

medicine_mean_price = [(k, sum(v) / len(v)) for k, v in medicine2price.items()]

medicine_mean_price = sorted(medicine_mean_price, key=lambda x: x[1], reverse=True)

medicine_mean_price_array = np.array(medicine_mean_price)
df = pd.DataFrame(medicine_mean_price_array, columns=["medicine", "mean price"])

df.to_excel('medicine_price.xlsx', index=False, header=True)


