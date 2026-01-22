import feedparser
import requests
import os

# GitHub Secrets에서 웹훅 주소를 가져옵니다.
WEBHOOK_URL = os.environ.get('MM_WEBHOOK_URL')
RSS_URL = "https://news.hada.io/rss/news"

def send_to_mattermost():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return

    # 최신글 1개 가져오기
    entry = feed.entries[0]
    title = entry.title
    link = entry.link
    
    # 매터모스트로 보낼 메시지 형식
    message = f"### 📰 GeekNews 최신 소식\n**[{title}]({link})**"
    
    payload = {"text": message}
    response = requests.post(WEBHOOK_URL, json=payload)
    
    if response.status_code == 200:
        print(f"Successfully posted: {title}")
    else:
        print(f"Failed to post. Status code: {response.status_code}")

if __name__ == "__main__":
    send_to_mattermost()