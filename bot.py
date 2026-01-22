import feedparser
import requests
import os
import re

WEBHOOK_URL = os.environ.get('MM_WEBHOOK_URL')
RSS_URL = "https://news.hada.io/rss/news"
DB_FILE = "last_link.txt"

def clean_html(raw_html):
    """HTML 태그를 제거하고 텍스트만 추출합니다."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def send_to_mattermost():
    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        return

    last_link = ""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            last_link = f.read().strip()

    new_entries = []
    for entry in feed.entries:
        if entry.link == last_link:
            break
        new_entries.append(entry)

    if not new_entries:
        print("새로운 소식이 없습니다.")
        return

    for entry in reversed(new_entries):
        # 1. 요약 내용 정리 (HTML 제거 및 3줄 제한)
        summary = clean_html(entry.summary)
        summary_lines = summary.split('\n')
        short_summary = "\n".join([line for line in summary_lines if line.strip()][:3])
        
        # 2. 메시지 구성 (제목 + 링크 + 요약)
        message = (
            f"### 📰 [GeekNews] {entry.title}\n"
            f"🔗 **링크:** {entry.link}\n\n"
            f"> {short_summary}..."
        )

        payload = {
            "username": "GeekNews Bot",
            "icon_url": "https://news.hada.io/favicon.ico",
            "text": message
        }
        
        requests.post(WEBHOOK_URL, json=payload)
        print(f"전송 완료: {entry.title}")

    with open(DB_FILE, "w") as f:
        f.write(feed.entries[0].link)

if __name__ == "__main__":
    send_to_mattermost()