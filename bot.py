import feedparser
import requests
import os
import re

WEBHOOK_URL = os.environ.get('MM_WEBHOOK_URL')
RSS_URL = "https://news.hada.io/rss/news"
DB_FILE = "last_link.txt"
MAX_FIRST_RUN_ENTRIES = 3

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.strip()

def send_to_mattermost():
    if not WEBHOOK_URL:
        print("오류: MM_WEBHOOK_URL 환경 변수가 설정되지 않았습니다.")
        return

    try:
        feed = feedparser.parse(RSS_URL)
    except Exception as e:
        print(f"오류: RSS 피드를 가져올 수 없습니다 - {e}")
        return

    if not feed.entries:
        print("오류: RSS 피드에 항목이 없습니다.")
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

    # 첫 실행 시 너무 많은 글 전송 방지
    if not last_link and len(new_entries) > MAX_FIRST_RUN_ENTRIES:
        new_entries = new_entries[:MAX_FIRST_RUN_ENTRIES]
        print(f"첫 실행: 최근 {MAX_FIRST_RUN_ENTRIES}개 글만 전송합니다.")

    for entry in reversed(new_entries):
        summary = clean_html(entry.summary)
        summary_lines = summary.split('\n')
        short_summary = "\n".join([line for line in summary_lines if line.strip()][:3])

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

        try:
            response = requests.post(WEBHOOK_URL, json=payload)
            if response.status_code == 200:
                print(f"전송 성공: {entry.title}")
            else:
                print(f"전송 실패: {entry.title} (상태 코드: {response.status_code})")
        except Exception as e:
            print(f"전송 오류: {entry.title} - {e}")

    with open(DB_FILE, "w") as f:
        f.write(feed.entries[0].link)

if __name__ == "__main__":
    send_to_mattermost()