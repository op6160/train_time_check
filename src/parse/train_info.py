from src.parse.constants import stationID as stations
from src.parse.parse_util import re_form
import os
import sys

from src.libs import logger

def find_station_by_id(id):
    """
    Find a station name and station's info by its id.
    Return: (station_name:str, station_info:dict)
    """
    for name, value in stations.items():
        if value["id"] == id:
            return name, value

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
            logger.info(f"warning: unknown train type. {train_type}.")
            logger.info(f" the logic will be worked as normal train type.")
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
    # find destination by class name "ressha_ikisaki"
    destination_tag = eki_n[0].find(class_="ressha_ikisaki")
    destination = destination_tag.text if destination_tag else "Unknown"

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