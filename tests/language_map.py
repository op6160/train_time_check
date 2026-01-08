import json
import re

def dict_replace(dictionary, replace_map):
    temp_str = json.dumps(dictionary, ensure_ascii=False)
    pattern = re.compile("|".join(map(re.escape, replace_map.keys())))
    temp_str = pattern.sub(lambda x: replace_map[x.group(0)], temp_str)
    return json.loads(temp_str)

ko_replace_map = {
    # 명사변환
    "normal": "보통",
    "kukankaisoku": "구간쾌속",
    "kaisoku": "쾌속",
    "shinkaisoku": "신쾌속",
    "tokubetsukaisoku": "특별쾌속",
    "up": "상행",
    "down": "하행",
    # 역명
    "豊橋":"도요하시",
    "西小坂井":"니시코자카이",
    "愛知御津":"아이치미토",
    "三河大塚":"미카와오오츠카",
    "三河三谷":"미카와미야",
    "蒲郡":"가마고오리",
    "三河塩津":"미카와시오츠",
    "三ヶ根":"산가네",
    "幸田":"코타",
    "相見":"아이미",
    "岡崎":"오카자키",
    "西岡崎":"니시오카자키",
    "安城":"안조",
    "三河安城":"미카와안조",
    "東刈谷":"히가시가리야",
    "野田新町":"노다신마치",
    "刈谷":"가리야",
    "逢妻":"아이즈마",
    "大府":"오부",
    "共和":"교와",
    "南大高":"미나미오다카",
    "大高":"오다카",
    "笠寺":"카사데라",
    "熱田":"아츠타",
    "金山":"가나야마",
    "尾頭橋":"오토바시",
    "名古屋":"나고야",
    "枇杷島":"비와지마",
    "清洲":"키요스",
    "稲沢":"이나자와",
    "尾張一宮":"오와리이치노미야",
    "木曽川":"키소가와",
    "岐阜":"기후",
    "西岐阜":"니시기후",
    "穂積":"호즈미",
    "大垣":"오가키",
    "垂井":"타루이",
    "関ケ原":"세키가하라",
    "柏原":"카시와라",
    "近江長岡":"오미나가오카",
    "醒ヶ井":"사메가이",
    "米原":"마이바라"
}

ja_replace_map = {
    "normal": "普通",
    "kukankaisoku": "区間快速",
    "kaisoku": "快速",
    "shinkaisoku": "新快速",
    "tokubetsukaisoku": "特別快速",
    "up": "上行",
    "down": "下行",
}

en_replace_map = {
    "kukankaisoku": "limited express",
    "kaisoku": "express",
    "shinkaisoku": "new express",
    "tokubetsukaisoku": "special express",
    "up": "Upper Line",
    "down": "Lower Line",
    "豊橋":"Toyohashi",
    "西小坂井":"NishiKozakai",
    "愛知御津":"Aichimito",
    "三河大塚":"MikawaOtsuka",
    "三河三谷":"MikawaMiya",
    "蒲郡":"Gamagoori",
    "三河塩津":"MikawaShiotsu",
    "三ヶ根":"Sangane",
    "幸田":"Kota",
    "相見":"Aimi",
    "岡崎":"Okazaki",
    "西岡崎":"NishiOkazaki",
    "安城":"Anjo",
    "三河安城":"MikawaAnjo",
    "東刈谷":"HigashiKariya",
    "野田新町":"NodaShimmachi",
    "刈谷":"Kariya",
    "逢妻":"Aizuma",
    "大府":"Obu",
    "共和":"Kyowa",
    "南大高":"MinamiOdaka",
    "大高":"Odaka",
    "笠寺":"Kasadera",
    "熱田":"Atsuta",
    "金山":"Kanayama",
    "尾頭橋":"Otobashi",
    "名古屋":"Nagoya",
    "枇杷島":"BiwaJima",
    "清洲":"Kiyosu",
    "稲沢":"Inazawa",
    "尾張一宮":"OwariIchinomiya",
    "木曽川":"Kisogawa",
    "岐阜":"Kifu",
    "西岐阜":"NishiKifu",
    "穂積":"Hozumi",
    "大垣":"Ogaki",
    "垂井":"Tarui",
    "関ケ原":"Sekigahara",
    "柏原":"Kashiwara",
    "近江長岡":"Ominagaoka",
    "醒ヶ井":"Samegai",
    "米原":"Maibara"
}

def ja_form():
    message_form = {
        "train_type":"列車",
        "destination":"行き",
        "from_station":"駅から出発し、",
        "before_station":"駅を通過、",
        "to_station":"へ移動中。",
        "rate_time":"分遅れ"
        }
    return message_form, ja_replace_map

def ko_form():
    message_form = {
        "train_type":"열차",
        "destination":"행",
        "from_station":"역 출발, ",
        "before_station":"역 통과, ",
        "to_station":"역 이동중",
        "rate_time":"분 지연"
        }
    return message_form, ko_replace_map

def en_form():
    message_form = {
        "train_type":"train",
        "destination":" going",
        "from_station":" from, ",
        "before_station":" via, ",
        "to_station":" to",
        "rate_time":" mins late"
    }
    return message_form, en_replace_map