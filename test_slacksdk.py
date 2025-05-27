import os, dotenv, time, datetime
from slack_sdk import WebClient
from pprint import pprint

dotenv.load_dotenv()

client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
# response = client.conversations_list()
# conversations = response["channels"]

# 원하는 날짜(예: 2025-05-27)
date_str = "2025-05-27"
start_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
end_dt = start_dt + datetime.timedelta(days=1)

oldest = time.mktime(start_dt.timetuple())
latest = time.mktime(end_dt.timetuple())

channel_id = os.getenv("ATTEND_CHANEL_ID")

# # 봇을 출석 채널에 초대
# rp = client.conversations_join(channel=channel_id)
# print(rp)

# 대화 조회
response = client.conversations_history(
    channel=channel_id,
    oldest=oldest,
    latest=latest,
    inclusive=True
    )
messages = response["messages"]
pprint(messages)