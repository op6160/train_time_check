# ======================================================================================= #
# * * * * * * code for test * * * * * * #
# mhtml using 
import email
from bs4 import BeautifulSoup
def parse_mhtml_to_soup(mhtml_content):
    """XXX: for tester code"""
    msg = email.message_from_string(mhtml_content)
    html_content = None
    # find text/html
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            # decode
            html_content = part.get_payload(decode=True)
            charset = part.get_content_charset()
            if charset:
                html_content = html_content.decode(charset, errors='replace')
            break
    
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup
    else:
        return None

with open("tests/dev.test.mhtml", 'r', encoding='utf-8') as f:
    mhtml_text = f.read()
    soup = parse_mhtml_to_soup(mhtml_text)
# * * * * * * = = = = = = = * * * * * * #
# ======================================================================================= #
from libs import get_html_content, log
from bs4 import BeautifulSoup
import re

# const
go_up_keyword = "【下り線】"
go_down_keyword = "【上り線】"

# text processing
def text_remove_whitespace(text):
    """'Remove whitespace' and 'replace newlines to whitespace' from a string."""
    text = text.replace(" ", "")
    text = text.replace("　", "")
    text = text.replace("\t", "")
    return text.strip()

def text_replace_newlines(text):
    """Replace newlines to whitespace."""
    text = text.replace("\n\n\n\n", " ")
    text = text.replace("\n\n\n", " ")
    text = text.replace("\n\n", " ")
    text = text.replace("\n", " ")
    return text

def text_normalizing_symbol(text):
    """Replace similar symbols to one symbol."""
    text = text.replace("～","~")
    text = text.replace("〜","~")
    text = text.replace("（","(")
    text = text.replace("）",")")
    return text

# list processing
def list_sort_by_titile(rate_info):
    """
    XXX: hard code.
    Sort rate info by title.

    Take a list of rate info and sort it by title.
    If the info starts with "【", it is considered as a title.
    Otherwise, it is considered as contents of the previous title.
    """
    result = []
    for info in rate_info:
        if info.startswith("【"):
            result.append(info)
        else:
            result[-1] += info
    return result

def re_form(startswith = "", endswith = ""):
    return re.compile(r'^'+startswith+r'*'+endswith)

def list_processing(soup):
    """
    XXX: hard code
    """
    rate_info = []
    targets = soup.find_all('div', id=re.compile(r'^unko_joho_shosai_\d+_naiyo'))
    targets = len(targets)
    if targets is None:
        raise ValueError("error: targets is None")
    for counting in range(targets):
        # get info div
        rate_info_div = soup.find("div", id = f"unko_joho_shosai_{counting}_naiyo")
        if rate_info_div is None:
            break
        # div to soup to get text
        rate_info_div_soup = BeautifulSoup(rate_info_div.prettify(), 'html.parser')
        # remove </br>
        for tag in rate_info_div_soup.find_all(["br"]):
            tag.decompose()
        # get text
        rate_info_div_soup_text = rate_info_div_soup.find("p").text
        # normalize the text
        rate_info_div_soup_text = text_remove_whitespace(rate_info_div_soup_text)
        rate_info_div_soup_text = text_replace_newlines(rate_info_div_soup_text)
        rate_info_div_soup_text = text_normalizing_symbol(rate_info_div_soup_text)
        # append to list
        rate_info.append(rate_info_div_soup_text)
    return rate_info

def split_rate_info(rate_info):
    """
    XXX: hard code
    Split rate info by keyword.
    """
    # init
    go_down_info = [] # morning
    go_up_info = [] # night

    # split
    for rate in rate_info:
        if go_up_keyword in rate:
            go_up_info.append(rate)

            if go_down_keyword in rate:
                if rate.find(go_up_keyword) > rate.find(go_down_keyword):
                    go_up_info[-1] = rate[rate.find(go_up_keyword):].strip()
                else:
                    go_up_info[-1] = rate[rate.find(go_up_keyword):rate.find(go_down_keyword)].strip()

        if go_down_keyword in rate:
            go_down_info.append(rate)

            if go_up_keyword in rate:
                if rate.find(go_up_keyword) < rate.find(go_down_keyword):
                    go_down_info[-1] = rate[rate.find(go_down_keyword):].strip()
                else:
                    go_down_info[-1] = rate[rate.find(go_down_keyword):rate.find(go_up_keyword)].strip()
    
    # add empty string to avoid go_up_title and go_down_title allocating error
    if len(go_up_info) == 0:
        log("warn: go_up_info is empty")
        go_up_info.append("")
    if len(go_down_info) == 0:
        log("warn: go_down_info is empty")
        go_down_info.append("")
    return go_down_info, go_up_info

def report_info_check(go_info:list, direction:str):
    """
    Check if there is keyword in the given info list.
    If there is, send email with data.
    """
    report_flag = False
    # set keywords to check (important: it must be opposite of direction and keyword)
    keyword = go_down_keyword if direction == "up" else go_up_keyword
    for info in go_info:
        if keyword in info:
            log(f"error: {keyword} detected in {direction} info: {info}")
            report_flag = True
    if report_flag:
        # Do: send email with data
        # TODO: implement email sending
        pass
    return

def write_state_message(go_info:list, direction:str):
    """
    XXX: hard code. format:
    【下り線】 ~~
    新快速～～行き（～～〇〇時〇〇分）快速～～行き（～～☓☓時☓☓分）
    """
    def it_is_not_taketoyo(message):
        """usecase"""
        return None if "武豊行き" in message else message
    # init
    state_message = ""
    # report check
    report_info_check(go_info, direction)
    # keyword set
    keyword = go_up_keyword if direction == "up" else go_down_keyword
    for idx, info in enumerate(go_info):
        message = text_remove_whitespace(info)
        if idx == 0:
            state_message = message+"\n"
            continue
        message = message.replace(keyword, "").strip()

        # filtering taketoyo line
        message = it_is_not_taketoyo(message)
        if not message:
            continue
        
        # one line one info formatting
        if message.count(")") > 1:
            message = message.replace(")", ")\n")
        else:
            message += "\n"
        state_message += message
    return state_message

# BASE_URL = "https://traininfo.jr-central.co.jp/"
# url = BASE_URL + "zairaisen/status_detail.html?line=10001"

# html = get_html_content(url)
# soup = BeautifulSoup(html, 'html.parser')

# get rate_info
rate_info = list_processing(soup)
rate_info = list_sort_by_titile(rate_info)

go_down_info, go_up_info = split_rate_info(rate_info)
go_down_title = go_down_info[0]
go_up_title = go_up_info[0]

# * * * * * * code for test * * * * * * #
# no parsed data 

print("*"*20)
print("rate_info: ")
for rate in rate_info:
    print(rate)
print("*"*20)
# if state == up
print("up down info")
log(write_state_message(go_up_info, "up"))
# if state == down
log(write_state_message(go_down_info, "down"))

# * * * * * * = = = = = = = * * * * * * #
####################################################################################################################

# logical flow
if go_down_title:
    # TODO: do direction down's data check
    pass
if go_up_title:
    # TODO: do direction up's data check
    pass

from station import stationID as stations

def find_station_by_id(id):
    for name, value in stations.items():
        if value["id"] == id:
            return name, value

def get_before_station(current_from_id, train_level, direction):
    # XXX: 데이터 구조를 잘못 설계해서, idx기반으로 구현했음
    values = list(stations.values())
    if direction == "up":
        if values[current_from_id]["level"] < train_level: #역의 레벨이 기차레벨보다 낮을 때
            return get_before_station(current_from_id - 1, train_level, direction)
    elif direction == "down":
        if values[current_from_id]["level"] < train_level:
            return get_before_station(current_from_id + 1, train_level, direction)
    keys = list(stations.keys())
    return keys[current_from_id]

def get_train_info(data):
    def get_train_type(data):
    # train_type_img = data.parent.find("img")["src"][:-4].split("/")[-1].split("_")[-1]
        train_type_img = data.parent.find("img")
        img_src = train_type_img["src"]
        src_filename = img_src[:-4]
        src_filename_nopath = src_filename.split("/")[-1]
        train_type = src_filename_nopath.split("_")[-1]
        return train_type

    def get_train_level(train_type):
        if train_type == "normal":
            return 0
        elif train_type == "kukankaisoku":
            return 1
        elif train_type == "kaisoku":
            return 2
        elif train_type == "shinkaisoku":
            return 3
        elif train_type == "tokubetsukaisoku":
            return 4
        else:
            return "unknown"

    def set_from_to_staion_id(tps):
        down_on_station_case = tps["on_station"] == "1" and tps["direction"] == "l"
        down_not_on_station_case = tps["on_station"] == "0" and tps["direction"] == "l"
        up_case = tps["direction"] == "r"

        if down_on_station_case:
            from_station_id = station_id + 1
            to_station_id = station_id
        elif down_not_on_station_case:
            from_station_id = station_id
            to_station_id = station_id - 1
        elif up_case:
            from_station_id = station_id
            to_station_id = station_id + 1
        else:
            raise Exception("Invalid train params")
        from_station_name, ___ = find_station_by_id(from_station_id)
        to_station_name, ___ = find_station_by_id(to_station_id)

        return from_station_name, to_station_name, from_station_id    
    
    # find id "eki_n" div
    eki_n = data.find_parents(id = re_form(r"eki_\d"))

    # raw data
    # get station info
    station_number_id = eki_n[-1]["id"]
    station_space_number_id = eki_n[1]["id"]
    # train rate time
    train_rate_time_str = data.text
    # train html id
    train_number_id = data["id"]

    # logical data
    # train_params : 1-l-1 -> on_station-direction-unknown
    train_params_string = train_number_id[-5:] # ex) 1-l-1
    tps = {"on_station": train_params_string[0],
            "direction": train_params_string[2],
            "unknown_value": train_params_string[4]}

    # processed data
    # get train info
    train_type = get_train_type(data)
    train_level = get_train_level(train_type)
    
    # get station name
    station_id = int(station_number_id.replace("eki_",""))
    station_name, ___ = find_station_by_id(station_id)

    # set diretion
    direction = "up" if tps["direction"] == "r" else "down"
    
    # get final destination
    destination = data.parent.find(id = re_form(r"ikisaki\d")).text

    # set from_station_id, to_station_id
    from_station_name, to_station_name, from_station_id = set_from_to_staion_id(tps)

    # get before station name
    before_station_name = None
    # if train_type != "normal":
    before_station_name = get_before_station(from_station_id, train_level, direction)

    # result data
    train_info_info = {
        "train_type":train_type, 
        "train_level":train_level, 
        "direction":direction, 
        "destination":destination, 
        "from_station_name":from_station_name, 
        "to_station_name":to_station_name,
        "train_rate_time_str":train_rate_time_str,
        "before_station_name":before_station_name
    }
    return train_info_info

def print_train_info(train_info_info):
    # get data from train info
    train_type = train_info_info["train_type"]
    train_level = train_info_info["train_level"]
    direction = train_info_info["direction"]
    destination = train_info_info["destination"]
    from_station_name = train_info_info["from_station_name"]
    to_station_name = train_info_info["to_station_name"]
    train_rate_time_str = train_info_info["train_rate_time_str"]
    before_station_name = train_info_info["before_station_name"]
    # print data
    print(train_type, train_level,end="\t")
    print(f"{direction}\t{destination}", end="\t")
    print(from_station_name, end="\t->\t")
    print(to_station_name, end="\t")
    # print(station_number_id+"\t:", end="\t")
    # print(station_space_number_id+"\t:", end="\t")
    # print(train_number_id+"\t:", end="\t")
    print(train_rate_time_str, end="\t")
    print(before_station_name)
    return  

    
rate_time_soup_find = soup.find_all("div", id = re_form("okure-jikan-ja", ""))
train_infos = {}
for idx, data in enumerate(rate_time_soup_find):
    if data.text:
        try:
            train_info_info = get_train_info(data)
            train_infos[str(idx)] = train_info_info
            print_train_info(train_info_info)

        except Exception as e:
            print(e)