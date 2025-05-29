import os, dotenv, time, datetime, json, re
from slack_sdk import WebClient
from collections import defaultdict

dotenv.load_dotenv()

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
# response = client.conversations_list()
# conversations = response["channels"]

# 날짜 설정
date_str = "2025-04-22"
start_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
end_dt = start_dt + datetime.timedelta(days=40)

oldest = time.mktime(start_dt.timetuple())
latest = time.mktime(end_dt.timetuple())

channel_id = os.getenv("ATTEND_CHANEL_ID")

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

json_data = json.dumps(all_messages, ensure_ascii=False, indent=4)
with open("all_messages.json", "w", encoding="utf-8") as f:
    f.write(json_data)


REQUIRED_VALUES  = {
    "username": "ZEP Notification",
    "bot_id": "B08NN84BQAK",
    "subtype": "bot_message",
    "type": "message"
}

fields = ['text', 'ts', 'username']
result = []

# 한글/영어 정규표현식 패턴
pattern_kr = r'(.+?)님이 임포스터에 (접속|접속을 종료)했습니다.\(userID: ([^)]+)\)'
pattern_en = r'(.+?) has (connected to|disconnected from) 임포스터.\(userID: ([^)]+)\)'

# 원하는 필드만 추가
for item in all_messages:
    # 1. 필수 필드 검증
    if not all(item.get(k) == v for k, v in REQUIRED_VALUES.items()):
        continue  # 조건 불일치시 건너뜀

    # 2. 필드 추출
    filtered = {key: item.get(key, None) for key in fields}
    text = filtered.get('text', '')

    # 기본값
    name, is_connect, user_id = None, None, None

    # text에서 이름, 접속여부, userid 분리 후 따로 저장
    match_kr = re.match(pattern_kr, text)
    match_en = re.match(pattern_en, text)
    if not (match_kr or match_en):
        continue  # 패턴 불일치시 건너뜀

    if match_kr:
        name = match_kr.group(1)
        is_connect = match_kr.group(2) == "접속"
        user_id = match_kr.group(3)
    elif match_en:
        name = match_en.group(1)
        is_connect = match_en.group(2) == "connected to"
        user_id = match_en.group(3)

    filtered['name'] = name
    filtered['is_connect'] = is_connect
    filtered['user_id'] = user_id

    result.append(filtered)

json_data = json.dumps(result, ensure_ascii=False, indent=2)
with open("all_attend.json", "w", encoding="utf-8") as f:
    f.write(json_data)


# 결과 누적 리스트
user_times = defaultdict(lambda: {"name": None, "user_id": None, "duration_seconds": 0.0})

# 연결 상태 추적용 딕셔너리 (key: user_id, value: connect_ts)
active_connections = {}

for item in result:
    user_id = item["user_id"]
    if not user_id:
        continue

    # 접속 이벤트
    if item["is_connect"]:
        active_connections[user_id] = float(item["ts"])
        user_times[user_id]["name"] = item["name"]
        user_times[user_id]["user_id"] = user_id

    # 종료 이벤트
    elif user_id in active_connections:
        connect_ts = active_connections.pop(user_id)
        disconnect_ts = float(item["ts"])
        duration = disconnect_ts - connect_ts
        user_times[user_id]["duration_seconds"] += duration

# 결과 리스트로 변환
accumulated = list(user_times.values())

def seconds_to_hm(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}시간 {minutes}분"

for entry in accumulated:
    entry["duration_hm"] = seconds_to_hm(entry["duration_seconds"])

json_data = json.dumps(accumulated, ensure_ascii=False, indent=2)
with open("attendance_summary.json", "w", encoding="utf-8") as f:
    f.write(json_data)