# 百度翻译

import requests

url = "https://fanyi.baidu.com/sug"

content = input("请输入需要翻译的词：")

data = {
    "kw": content,
}

response = requests.post(url, data=data)

result = response.json()

print(result)

response.close()


