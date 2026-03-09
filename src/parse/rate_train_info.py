from src.libs import get_html_content, logger
from bs4 import BeautifulSoup
import re
from config import (
    go_up_keyword,
    go_down_keyword,
    fine_keyword,
    BASE_URL,
    STATE_URL,
    MESSAGE_URL,
)
from src.parse.train_info import get_train_info
from src.parse.parse_util import (
    re_form,
    text_remove_whitespace,
    text_replace_newlines,
    text_normalizing_symbol,
    soup_find_all_div_by_id
)

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
        TODO: this function should be refactored.
        Get train driving state from the given new source. train_information.html
        """
        return {
            "rate_info": [],
            "driving_state_train": False,
            "driving_state_title": "",
        }
        # rate_info = []
        # targets = soup.find_all('div', id=re.compile(r'^unko_joho_shosai_\d+_naiyo'))
        # targets = len(targets)
        # if targets is None:
        #     raise ValueError("error: targets is None")

        # # get train driving state
        # state_title = soup.find("p", "shosai-bun").text
        # if state_title is None:
        #     raise ValueError("error: state_title is None")
        # elif fine_keyword == state_title:
        #     # driving state is fine
        #     state_train = True
        # else:
        #     state_train = False

        # if not state_train:
        #     for counting in range(targets):
        #         # get info div
        #         rate_info_div = soup.find("div", id = f"unko_joho_shosai_{counting}_naiyo")
        #         if rate_info_div is None:
        #             break
        #         # div to soup to get text
        #         rate_info_div_soup = BeautifulSoup(rate_info_div.prettify(), 'html.parser')
        #         # remove </br>
        #         for tag in rate_info_div_soup.find_all(["br"]):
        #             tag.decompose()
        #         # get text
        #         rate_info_div_soup_text = rate_info_div_soup.find("p").text
        #         # normalize the text
        #         rate_info_div_soup_text = text_remove_whitespace(rate_info_div_soup_text)
        #         rate_info_div_soup_text = text_replace_newlines(rate_info_div_soup_text)
        #         rate_info_div_soup_text = text_normalizing_symbol(rate_info_div_soup_text)
        #         # append to list
        #         rate_info.append(rate_info_div_soup_text)
        # return {
        #     "rate_info": rate_info,
        #     "driving_state_train": state_train,
        #     "driving_state_title": state_title
        # }
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
                logger.info("go_up_info is empty")
                go_up_info.append("")
            if len(go_down_info) == 0:
                logger.info("go_down_info is empty")
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
    html = get_html_content(url = url, load_time = 3)
    soup = BeautifulSoup(html, 'html.parser')
    message_url = BASE_URL + MESSAGE_URL
    message_html = get_html_content(url = message_url, load_time = 3)
    message_soup = BeautifulSoup(message_html, 'html.parser')

    train_data = flow(soup)

    # get notice
    train_state_data = get_driving_state(message_soup)
    state_train = train_state_data["driving_state_train"]
    state_title = train_state_data["driving_state_title"]
    rate_info = train_state_data["rate_info"]

    if state_train:
        return state_train, state_title, None

    rate_info = list_sort_by_titile(rate_info)
    notice_data = notice_data_packing(rate_info)

    return state_train, notice_data, train_data

def on_train_data_parse(position_info, on_train_data, train_in):
    for station_idx, position_info_item in enumerate(position_info):
        for idx, parent in enumerate(position_info_item):
            if parent.name is None:
                continue
            direction = "up" if idx == 0 else "down"
            station_id = station_idx - 1 if direction == "down" else station_idx
            found_child = parent.select(".position-item__img")
            if not found_child:
                continue
            for child in parent:
                if child.name is None: # 태그가 아니면(문자열이면) 스킵
                    continue

            if found_child and station_id != -1:
                for child in found_child:
                    on_train_data[str(station_id)].append({
                        "direction": direction,
                        "train_in": train_in,
                        "data": child.parent,
                    })
    return on_train_data

def train_data_parse(on_train_data):
    """train_data ( dict ): train data
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
    train_data = {}
    for station_id, data in on_train_data.items():
        if not data:
            continue

        for idx, item in enumerate(data):
            from src.parse.train_info import get_train_level
            from src.parse.parse_util import multi_replace
            from src.parse.constants import NEW_TRAIN_TYPE
            train_type = multi_replace(get_train_type(item["data"]), NEW_TRAIN_TYPE)
            train_level = get_train_level(train_type)
            direction = item["direction"]
            destination = item["data"].find(class_=re.compile("to-station")).get_text(strip=True)
            station_id = int(station_id)
            tps = {
                "on_station": "1" if item["train_in"] == "on" else "0",
                "direction": "r" if direction == "up" else "l",
                "unknown_value": ""
            }
            from src.parse.train_info import set_from_to_staion_id, get_before_station
            from_station_name, to_station_name, from_station_id = set_from_to_staion_id(tps, station_id)
            from_station_name = 1
            before_station_name, before_station_id = get_before_station(from_station_id, train_level, direction)
            train_rate_time_str = item["data"].find(class_="delay-time").get_text(strip=True)
            unit_data = {
                "train_type": train_type,
                "train_level": train_level,
                "direction": direction,
                "destination": destination,
                "from_station_name": from_station_name,
                "to_station_name": to_station_name,
                "train_rate_time_str": "",
                "before_station_name": before_station_name,
                "before_station_id": before_station_id,
            }
            train_data[station_id] = unit_data
    return train_data

def get_train_type(data):
    train_type_img = data.select("img.position-item__img")
    src = train_type_img[0]["src"]
    src_filename = src.split("/")[-1][:-4]
    train_type = src_filename.replace("_r_position", "")
    return train_type

def flow(soup):
    # station object idx is refer to as stations id.

    on_station = soup.find_all("div", class_ = "position-info-header")
    over_station = soup.find_all("div", class_ = "position-info-contents")
    
    on_train_data = {
        str(idx): []
        for idx in range(len(on_station))
    }

    on_train_data = on_train_data_parse(on_station, on_train_data, "on")
    on_train_data = on_train_data_parse(over_station, on_train_data, "over")

    train_data = train_data_parse(on_train_data)

    # for key, value in train_data.items():
    #     if not value:
    #         continue
    #     for idx, item in enumerate(value):
    #         if item["train_in"] == "on":

    return train_data
    
def get_subobject_by_xpath_from_soup(soup, xpath) -> BeautifulSoup:
    path = "main"
    subpath_list = xpath.replace("/html/body/main/", "").split("/")
    for subpath in subpath_list:
        if subpath == "":
            continue
        if subpath.endswith("]"):
            object, index = subpath.split("[")
            index = index.replace("]", "")
            try:
                int(index)
            except TypeError as e:
                raise TypeError(f"error: It seems that xpath is not valid.\n  detail: {e}")
        path += " > " + object + f":nth-of-type({index})"

    return soup.select_one(path)
    

if __name__ == "__main__":
    get_train_rate_and_time_info()