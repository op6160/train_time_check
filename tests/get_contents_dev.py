from libs import get_html_content, log
from bs4 import BeautifulSoup
import re

from station import stationID as stations

# const
go_up_keyword = "【下り線】"
go_down_keyword = "【上り線】"
fine_keyword = "平常に運転しております。"
BASE_URL = "https://traininfo.jr-central.co.jp/"
STATE_URL = "zairaisen/status_detail.html?line=10001"
url = BASE_URL + STATE_URL


# text processing utility
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

def re_form(startswith = "", endswith = ""):
    return re.compile(r'^'+startswith+r'*'+endswith)


# data processing utility 
def find_station_by_id(id):
    """
    Find a station name and station's info by its id.
    Return: (station_name:str, station_info:dict)
    """
    for name, value in stations.items():
        if value["id"] == id:
            return name, value

def soup_find_all_div_by_id(soup, id):
    return soup.find_all("div", id = id)

# data processing
def get_train_info(data):
    """
    Get train info from the given html source.

    Args:
        data (BeautifulSoup object ): html source

    Returns:
        train_info_info ( dict ): train info
            {
                "train_type":str, 
                "train_level":int, 
                "direction":str, 
                "destination":str, 
                "from_station_name":str, 
                "to_station_name":str,
                "train_rate_time_str":str,
                "before_station_name":str
            }
    """
    def get_train_type(data):
        """
        Get the train type from the html source(img file name).

        """
        # train_type_img = data.parent.find("img")["src"][:-4].split("/")[-1].split("_")[-1]
        train_type_img = data.parent.find("img")
        img_src = train_type_img["src"]
        src_filename = img_src[:-4]
        src_filename_nopath = src_filename.split("/")[-1]
        train_type = src_filename_nopath.split("_")[-1]
        return train_type

    def get_train_level(train_type:str)->int:
        """
        Get the train level from the given train type.
        """
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
            log(f"warning: unknown train type. {train_type}.")
            log(f" the logic will be worked as normal train type.")
            return 0

    def set_from_to_staion_id(tps):
        """
        Set from_station_id and to_station_id based on the given train params.

        Args:
            tps ( dict ): train params

        Returns:
            from_station_name ( str ): from station name
            to_station_name ( str ): to station name
            from_station_id ( int ): from station id to use in get_before_station
        """
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

    def get_before_station(current_from_id, train_level, direction):
        """
        Find a before stop station name by train,station level.
        """
        # XXX: 데이터 구조를 잘못 설계해서, idx기반으로 구현했음
        values = list(stations.values())
        if direction == "up":
            if values[current_from_id]["level"] < train_level: #역의 레벨이 기차레벨보다 낮을 때
                return get_before_station(current_from_id - 1, train_level, direction)
        elif direction == "down":
            if values[current_from_id]["level"] < train_level:
                return get_before_station(current_from_id + 1, train_level, direction)
        keys = list(stations.keys())
        station_name = keys[current_from_id]
        station_id = str(stations[station_name]["id"])
        return station_name, station_id

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

    # get before station info
    before_station_name = None
    before_station_id = None
    # if train_type != "normal":
    before_station_name, before_station_id = get_before_station(from_station_id, train_level, direction)
    
    # result data packing
    train_info_info = {
        "train_type":train_type, 
        "train_level":train_level, 
        "direction":direction, 
        "destination":destination, 
        "from_station_name":from_station_name, 
        "to_station_name":to_station_name,
        "train_rate_time_str":train_rate_time_str,
        "before_station_name":before_station_name,
        "before_station_id":before_station_id
    }
    return train_info_info

# developing function
def write_state_message(go_info:list, direction:str):
    """
    XXX: hard code. format:
    【下り線】 ~~
    新快速～～行き（～～〇〇時〇〇分）快速～～行き（～～☓☓時☓☓分）
    """
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

# main function
def get_train_rate_and_time_info():
    """
    Get train rate and time information from the given html source.

    Returns:
        notice_data ( dict ): notice data
            {
                "go_down_title":str, 
                "go_down_info":list, 
                "go_up_title":str, 
                "go_up_info":list, 
                "_rate_info":list
            }
        train_data ( dict ): train data
            {
                "idx":dict, 
                    {
                        "train_type":str, 
                        "train_level":int, 
                        "direction":str, 
                        "destination":str, 
                        "from_station_name":str, 
                        "to_station_name":str,
                        "train_rate_time_str":str,
                        "before_station_name":str,
                        "before_station_id":str
                    }
            }
    """
    def get_driving_state(soup):
        """
        XXX: hard code
        """
        rate_info = []
        targets = soup.find_all('div', id=re.compile(r'^unko_joho_shosai_\d+_naiyo'))
        targets = len(targets)
        if targets is None:
            raise ValueError("error: targets is None")

        # get train driving state
        state_title = soup.find("p", "shosai-bun").text
        if state_title is None:
            raise ValueError("error: state_title is None")
        elif fine_keyword == state_title:
            # driving state is fine
            state_train = True
        else:
            state_train = False

        if not state_train:
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
        return {
            "rate_info": rate_info,
            "driving_state_train": state_train,
            "driving_state_title": state_title
        }
    def notice_data_packing(rate_info):
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

        go_down_info, go_up_info = split_rate_info(rate_info)

        go_down_title = go_down_info[0]
        go_up_title = go_up_info[0]
        go_down_info = go_down_info[1:]
        go_up_info = go_up_info[1:]

        notice_data = {
        "go_down_title": go_down_title,
        "go_down_info": go_down_info,
        "go_up_title": go_up_title,
        "go_up_info": go_up_info,
        "_rate_info": rate_info
        }
        return notice_data
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


    # get html
    url = BASE_URL + STATE_URL
    html = get_html_content(url)
    soup = BeautifulSoup(html, 'html.parser')

    # test html
    # import email
    # FILE2 = "tests/mhtml/dev.1205.mhtml"
    # with open(FILE2, 'r', encoding='utf-8') as f:
    #     mhtml_text = f.read()
    # def parse_mhtml_to_soup(mhtml_content):
    #     """XXX: for tester code"""
    #     msg = email.message_from_string(mhtml_content)
    #     html_content = None
    #     # find text/html
    #     for part in msg.walk():
    #         if part.get_content_type() == 'text/html':
    #             # decode
    #             html_content = part.get_payload(decode=True)
    #             charset = part.get_content_charset()
    #             if charset:
    #                 html_content = html_content.decode(charset, errors='replace')
    #             break
        
    #     if html_content:
    #         soup = BeautifulSoup(html_content, 'html.parser')
    #         return soup
    #     else:
    #         return None
    # soup = parse_mhtml_to_soup(mhtml_text)

    # get notice
    train_state_data = get_driving_state(soup)
    state_train = train_state_data["driving_state_train"]
    state_title = train_state_data["driving_state_title"]
    rate_info = train_state_data["rate_info"]

    if state_train:
        return state_train, state_title, None

    rate_info = list_sort_by_titile(rate_info)
    notice_data = notice_data_packing(rate_info)

    # get rate train times
    rate_time_soup_find = soup_find_all_div_by_id(soup, re_form("okure-jikan-ja", ""))
    train_data = {}

    for idx, data in enumerate(rate_time_soup_find):
        if data.text:
            train_info_info = get_train_info(data)
            train_data[str(idx)] = train_info_info
    return state_train, notice_data, train_data

def write_state_message(language, train_data, notice_data, direction=None):
    """
    Write state message in the given language.

    Args:
        language (str): the language to write in.
        train_data (dict): the train data to write.
        notice_data (dict): the notice data to write.
        direction ("up" or "down", optional): the direction to write. If not given, write all data. 
    """
    def gen_message(info, message_form):
        message = f'[{info["train_type"]}][{info["direction"]} {info["destination"]}{message_form["destination"]}] {info["train_rate_time_str"][1:]}{message_form["rate_time"]}\n'
        if info["from_station_name"] == info["before_station_name"]:
            message += f'"{info["from_station_name"]}"{message_form["from_station"]}"{info["to_station_name"]}"{message_form["to_station"]}'
        else:
            message += f'"{info["from_station_name"]}"{message_form["from_station"]}"{info["before_station_name"]}"{message_form["before_station"]}"{info["to_station_name"]}"{message_form["to_station"]}'
        return message

    def set_language_form(language):
        if language == "en":
            from language_map import en_form
            return en_form()
        elif language == "ko":
            from language_map import ko_form
            return ko_form()
        elif language == "ja":
            from language_map import ja_form
            return ja_form()
        else:
            raise ValueError("error: language is not supported")

    message_form, replace_map = set_language_form(language)
    from language_map import dict_replace
    train_data = dict_replace(train_data, replace_map)

    notice_message = "* notice:"
    train_message = []

    if direction in ("up", "down"):
        direction_title = f"go_{direction}_title"
        direction_info = f"go_{direction}_info"
        notice_message += f"{notice_data[direction_title]}" if notice_data[direction_title] else ""
        notice_message += "\n" if notice_data[direction_title] and notice_data[direction_info] else ""
        notice_message += f"{notice_data[direction_info]}" if notice_data[direction_info] else ""
        if notice_message == "* notice:": notice_message = ""
        for info in train_data.values():
            if info["direction"] == replace_map[direction]:
                train_message.append(gen_message(info, message_form))

    else:
        for msg in notice_data.values():
            notice_message += f"{msg}" if msg else ""
        for info in train_data.values():
            train_message.append(gen_message(info, message_form))

    if notice_message == "* notice:": notice_message = ""
    return notice_message, train_message

def print_message(notice_message, train_message):
    print("*" * 20)
    print(notice_message)
    print("*" * 20)
    for message in train_message:
        print(message)
    print("*" * 20)

def main():
    state_train, notice_data, train_data = get_train_rate_and_time_info()
    if state_train:
        # fine state.
        print(notice_data)
        log("All trains are fine.")
    else:
        notice_message, train_message = write_state_message("ko", train_data, notice_data, "down")
        print_message(notice_message, train_message)

if __name__ == "__main__":
    main()