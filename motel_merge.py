import json
import requests
import pandas as pd
import os

###########모텔 json 파일 합치기

# 합치려는 JSON 파일들이 있는 폴더
directory_path = './mdata/'

# 모든 JSON 파일 목록을 가져옴
json_files = [f for f in os.listdir(directory_path) if f.endswith('.json')]

merged_data = []

for json_file in json_files:
    with open(os.path.join(directory_path, json_file), 'r', encoding='utf-8') as file:
        data = json.load(file)
        merged_data.extend(data)

# '숙소번호' 재정의 및 전체 숙소 넘버링
for index, motel in enumerate(merged_data, start=1):
    motel['숙소번호'] = index

# 합친 및 넘버링된 데이터를 새 JSON 파일에 저장
with open(os.path.join(directory_path, 'merged_mlist.json'), 'w', encoding='utf-8') as file:
    json.dump(merged_data, file, ensure_ascii=False, indent=4)

print(f"{len(json_files)}개의 JSON 파일이 'merged_mlist.json'에 합쳐졌습니다.")

########### 평점순+좌표 딕셔너리 추가

with open('mdata/merged_mlist.json', 'r', encoding='utf-8') as f:
    motel = json.load(f)

# 주소를 좌표로 바꾸는 함수
def addr_to_lat_lon(addr):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query={address}'.format(address=addr)
    headers = {"Authorization": "KakaoAK 2ee81ea57d8a4da7331e8a42e4b20ded"}
    result = json.loads(str(requests.get(url, headers=headers).text))
    match_first = result['documents'][0]['address']
    return float(match_first['x']), float(match_first['y'])

for i in range(len(motel)): # 지번주소가 섞여있을시 제거
    split=[]
    if motel[i]['주소'].endswith(']'):
        split = motel[i]['주소'].split('[') # split은 리스트 반환
        motel[i]['주소'] = split[0]

# 평점순, 좌표 딕셔너리 추가
for i in range(len(motel)):
    평점순 = {}
    평점순['친절도순'] = round((float(motel[i]['평점']['친절도'])*1.5+float(motel[i]['평점']['청결도'])+float(motel[i]['평점']['편의성'])+float(motel[i]['평점']['비품만족도']))*2/9, 2)
    평점순['청결도순'] = round((float(motel[i]['평점']['친절도'])+float(motel[i]['평점']['청결도'])*1.5+float(motel[i]['평점']['편의성'])+float(motel[i]['평점']['비품만족도']))*2/9, 2)
    평점순['편의성순'] = round((float(motel[i]['평점']['친절도'])+float(motel[i]['평점']['청결도'])+float(motel[i]['평점']['편의성'])*1.5+float(motel[i]['평점']['비품만족도']))*2/9, 2)
    평점순['비품만족도순'] = round((float(motel[i]['평점']['친절도'])+float(motel[i]['평점']['청결도'])+float(motel[i]['평점']['편의성'])+float(motel[i]['평점']['비품만족도'])*1.5)*2/9, 2)
    motel[i]['평점순']=평점순

    좌표 = {}
    address = motel[i]['주소']
    latlon = addr_to_lat_lon(address)
    좌표['위도'] = latlon[1]
    좌표['경도'] = latlon[0]
    motel[i]['좌표']=좌표


with open('motel_list_last.json', 'w', encoding='utf-8') as f:
    json.dump(motel, f, ensure_ascii=False, indent=4)


############ 좌표 확인
for i in range(len(motel)):
    latlon = motel[i]['좌표']
    print(i, latlon)