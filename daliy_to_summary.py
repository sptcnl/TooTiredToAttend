from pathlib import Path
import re, json

folder_path = Path('./daliy_attend')

# 모든 파일(폴더 포함)
all_items = list(folder_path.iterdir())
# 파일만
files_only = [f for f in folder_path.iterdir() if f.is_file()]
file_names = [f.name for f in files_only]
print(file_names)

def extract_date(filename):
    # 파일명에서 'YYYY.MM.DD' 패턴을 추출하여 (YYYY, MM, DD) 튜플로 반환
    m = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', filename)
    if m:
        y, m1, d = m.groups()
        return (int(y), int(m1), int(d))
    return (0, 0, 0)  # 패턴 못 찾으면 가장 앞에 오게

sorted_file_names = sorted(file_names, key=extract_date)
print(sorted_file_names)

merged_data = {}

for _ in range(len(sorted_file_names)):
    file_name = sorted_file_names.pop()
    print(file_name)
    file_path = folder_path / file_name

    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)

    for user_id, user_dates in data.items():
        # merged_data에 해당 사용자가 없으면 새로 만들기
        if user_id not in merged_data:
            merged_data[user_id] = {}

        # 앞에 있던 데이터
        front_data = merged_data[user_id]
        back_data = user_dates

        # 뒤에만 있는 날짜만 골라서 추가
        new_dates = set(back_data.keys()) - set(front_data.keys())
        new_records = {date: back_data[date] for date in new_dates}

        front_data.update(new_records)

def sort_by_date(data):
    result = {}
    for user, dates_dict in data.items():
        # dates_dict는 날짜: 값 딕셔너리
        sorted_dates = dict(sorted(dates_dict.items(), key=lambda x: x[0]))
        result[user] = sorted_dates
    return result

result = sort_by_date(merged_data)

output_path = folder_path / 'merged_daily_attend.json'
json_data = json.dumps(result, ensure_ascii=False, indent=2)


with open(output_path, 'w', encoding='utf-8') as f:
    f.write(json_data)


with open((folder_path / 'merged_daily_attend.json'), encoding='utf-8') as f:
    json_data = json.load(f)
    # print(json_data)

attend_sum = {}

for user, dates_dict in json_data.items():
    total_minutes = 0
    for time_str in dates_dict.values():
        m = re.match(r'(\d+)시간\s+(\d+)분', time_str)
        if m:
            hours = int(m.group(1))
            minutes = int(m.group(2))
            total_minutes += hours * 60 + minutes

    # total_minutes를 시간과 분으로 나누기
    total_hours = total_minutes // 60
    leftover_minutes = total_minutes % 60

    # "00시간 00분" 문자열로 변환
    time_sum_str = f"{total_hours:02d}시간 {leftover_minutes:02d}분"
    attend_sum[user] = time_sum_str

    output_path = folder_path / 'attend_sum.json'
    json_data = json.dumps(attend_sum, ensure_ascii=False, indent=2)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(json_data)

# print(json.dumps(json_data, ensure_ascii=False, indent=2))