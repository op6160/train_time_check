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
from src.parse.parse_util import (
    re_form,
    text_remove_whitespace,
    text_replace_newlines,
    text_normalizing_symbol,
    soup_find_all_div_by_id
)

# train info
from src.parse.train_info import get_train_level, get_train_type
from src.parse.parse_util import multi_replace
from src.parse.constants import NEW_TRAIN_TYPE
from src.parse.train_info import set_from_to_staion_id, get_before_station

# notice info
from src.parse.notice_info import get_driving_state, notice_data_packing, list_sort_by_titile

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
    # get train data 
    url = BASE_URL + STATE_URL
    html = get_html_content(url = url, load_time = 3)
    soup = BeautifulSoup(html, 'html.parser')
    
    # get notice data
    message_url = BASE_URL + MESSAGE_URL
    message_html = get_html_content(url = message_url, load_time = 3)
    message_soup = BeautifulSoup(message_html, 'html.parser')
    
    # notice data parse
    state_train, notice_data, state_title = notice_data_flow(message_soup)

    # no rate data
    if state_train:
        return state_train, state_title, None

    # train data parse
    train_data = train_data_flow(soup)
    return state_train, notice_data, train_data

def notice_data_flow(soup):
    """
    Parse notice data from the soup.

    Returns:
        state_train ( bool ): train state
        notice_data ( dict ): notice data
            {
                "go_down_title":str, 
                "go_down_info":list, 
                "go_up_title":str, 
                "go_up_info":list, 
                "_rate_info":list
            }
        state_title ( str ): webhook message title
    """
    train_state_data = get_driving_state(soup)
    # train state
    state_train = train_state_data["driving_state_train"]
    # webhook message title
    state_title = train_state_data["driving_state_title"]
    
    # no rate data
    if state_train:
        return state_train, "_", state_title
    
    # get notice data
    rate_info = train_state_data["rate_info"]
    # processing
    rate_info = list_sort_by_titile(rate_info)
    notice_data = notice_data_packing(rate_info)
    return state_train, notice_data, state_title

def on_train_data_parse(position_info, on_train_data, train_in):
    # train_in: "on" or "over"
    """
    Parse position info data and store it in on_train_data.

    Args:
        position_info (list): list of position info objects
        on_train_data (dict): dictionary to store parsed data
        train_in (str): either "on" or "over"

    Returns:
        on_train_data (dict): parsed data
    """
    for station_idx, position_info_item in enumerate(position_info):
        for idx, parent in enumerate(position_info_item):
            if parent.name is None:
                continue
            direction = "down" if idx == 0 else "up"
            station_id = station_idx if direction == "up" else station_idx
            found_child = parent.select(".position-item__img")
            if not found_child:
                continue
            
            # 2_or_more train (it happens when there is a lack of space on the website.)
            overchild = None
            for element in found_child:
                if "2_or_more" in element.get("src"):
                    overchild = element

            if found_child and station_id != -1:
                for child in found_child:
                    on_train_data[str(station_id)].append({
                        "direction": direction,
                        "train_in": train_in,
                        "data": child.parent,
                    })
            if overchild:
                childs = overchild.select(".position-info__popup .position-item")
                for child in childs:
                    on_train_data[str(station_id)].append({
                    "direction": direction,
                    "train_in": train_in,
                    "data": child.parent,
                })

            # print(on_train_data)
    return on_train_data

def train_data_parse(on_train_data):
    """
    Parse train data from the given on_train_data.

    Args:
        on_train_data ( dict ): on train data

    Returns:
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
    train_data = {}
    for station_id, data in on_train_data.items():
        if not data:
            continue

        for idx, item in enumerate(data):
            train_type = multi_replace(get_train_type(item["data"]), NEW_TRAIN_TYPE)
            if train_type == "2_or_more":
                continue
            train_level = get_train_level(train_type)
            direction = item["direction"]
            destination = item["data"].find(class_=re.compile("to-station")).get_text(strip=True)
            station_id = int(station_id)
            tps = {
                "on_station": "1" if item["train_in"] == "on" else "0",
                "direction": "r" if direction == "up" else "l",
                "unknown_value": ""
            }
            
            from_station_name, to_station_name, from_station_id = set_from_to_staion_id(tps, station_id)
            before_station_name, before_station_id = get_before_station(from_station_id, train_level, direction)
            train_rate_time_str = item["data"].find(class_="delay-time").get_text(strip=True)
            unit_data = {
                "train_type": train_type,
                "train_level": train_level,
                "direction": direction,
                "destination": destination,
                "from_station_name": from_station_name,
                "to_station_name": to_station_name,
                "train_rate_time_str": train_rate_time_str,
                "before_station_name": before_station_name,
                "before_station_id": before_station_id,
            }
            train_data[station_id] = unit_data
    return train_data


def train_data_flow(soup):
    """
    Parse train data from the given soup object.

    Args:
        soup ( BeautifulSoup ): Soup object

    Returns:
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
    on_station = soup.find_all("div", class_ = "position-info-header")
    over_station = soup.find_all("div", class_ = "position-info-contents")
    
    on_train_data = {
        str(idx): []
        for idx in range(len(on_station))
    }

    on_train_data = on_train_data_parse(on_station, on_train_data, "on")
    on_train_data = on_train_data_parse(over_station, on_train_data, "over")

    train_data = train_data_parse(on_train_data)
    return train_data