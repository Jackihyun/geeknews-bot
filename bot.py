import feedparser
import requests
import os

# 환경 변수 및 설정
WEBHOOK_URL = os.environ.get('MM_WEBHOOK_URL')
RSS_URL = "https://news.hada.io/rss/news"
DB_FILE = "last_link.txt"

def send_to_mattermost():
    # 1. RSS 피드 파싱
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        print("피드를 읽어올 수 없습니다.")
        return

    # 2. 이전에 저장된 마지막 링크 읽기
    last_link = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            last_link = f.read().strip()

    # 3. 새 글 필터링 (최신순이므로 역순으로 검사하여 새 글만 수집)
    new_entries = []
    for entry in feed.entries:
        if entry.link == last_link:
            break
        new_entries.append(entry)

    if not new_entries:
        print("새로운 소식이 없습니다.")
        return

    # 4. 새 글 전송 (오래된 새 글부터 순서대로 전송)
    for entry in reversed(new_entries):
        message = f"### 📰 GeekNews 새 소식\n**[{entry.title}]({entry.link})**"
        payload = {
            "username": "GeekNews Bot",
            "icon_url": "https://news.hada.io/favicon.ico",
            "text": message
        }
        requests.post(WEBHOOK_URL, json=payload)
        print(f"전송 완료: {entry.title}")

    # 5. 마지막 링크 파일 업데이트
    with open(DB_FILE, "w") as f:
        f.write(feed.entries[0].link)

if __name__ == "__main__":
    send_to_mattermost()