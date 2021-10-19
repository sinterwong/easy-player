# 豆瓣（数据懒得提取了）

import requests
from requests.models import Response
import time

url = "https://movie.douban.com/j/chart/top_list"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
}


for i in range(0, 100, 20):
    params = {
        "type": 24,
        "interval_id": "100:90",
        "action": "",
        "start": i,
        "limit": 20,
    }

    response = requests.get(url, params=params, headers=headers)
    print(response.headers)

    print(response.json())

    response.close()
    time.sleep(1)