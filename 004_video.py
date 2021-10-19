# 抓取梨视频网站视频（单条示例）
import requests

url = "https://www.pearvideo.com/video_1703167"

video_id = url.split("_")[-1]

video_status = f"https://www.pearvideo.com/videoStatus.jsp?contId={video_id}&mrd=0.6749847016967416"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36", 
    # 防盗链
    "Referer": "https://www.pearvideo.com/video_1703167"
}

response = requests.get(video_status, headers=headers)

result = response.json()

systemTime = result["systemTime"]
video_url = result["videoInfo"]["videos"]["srcUrl"]

true_url = video_url.replace(systemTime, "cont-{}".format(video_id))

print(true_url)

response.close()

