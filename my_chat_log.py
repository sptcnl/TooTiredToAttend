import os, dotenv, time, json, re
from datetime import datetime, timedelta
from slack_sdk import WebClient
from collections import defaultdict

dotenv.load_dotenv()

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
# response = client.conversations_list()
# conversations = response["channels"]
# print(conversations)

# 날짜 설정
date_str = "2024-12-12"
start_dt = datetime.strptime(date_str, "%Y-%m-%d")
end_dt = start_dt + timedelta(days=180)

oldest = time.mktime(start_dt.timetuple())
latest = time.mktime(end_dt.timetuple())

channel_id = os.getenv("LOUNGE_CHANEL_ID")
my_slack_id = os.getenv("MY_SLACK_ID")

def is_valid_message(msg):
    return (
        msg.get("user") == my_slack_id and
        msg.get("type") == "message" and
        "subtype" not in msg and
        "text" in msg and
        bool(msg["text"].strip()) and
        not re.fullmatch(r":\w+:", msg["text"].strip())
    )

# 모든 메시지 가져오기
all_messages = []
next_cursor = None

while True:
    params = {
        "channel": channel_id,
        "oldest": oldest,
        "latest": latest,
        "inclusive": True,
        "limit": 1000,  # 최대 1000개
    }
    if next_cursor:
        params["cursor"] = next_cursor

    response = client.conversations_history(**params)
    messages = response.get("messages", [])
    all_messages.extend(messages)

    # 다음 페이지가 있으면 next_cursor로 반복, 없으면 종료
    if response.get("has_more"):
        next_cursor = response.get("response_metadata", {}).get("next_cursor")
        if not next_cursor:
            break
        # Slack API rate limit 방지
        time.sleep(1)
    else:
        break
all_messages.sort(key=lambda x: float(x["ts"]))
valid_messages = [msg for msg in all_messages if is_valid_message(msg)]

json_data = json.dumps(valid_messages, ensure_ascii=False, indent=4)
with open("my_messages_in_lounge_channel.json", "w", encoding="utf-8") as f:
    f.write(json_data)