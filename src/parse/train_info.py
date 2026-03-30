from src.parse.station_map import stationID as stations

import os
import sys

import re
from src.parse.parse_util import multi_replace
from src.parse.station_map import NEW_TRAIN_TYPE

from src.libs import logger

def find_station_by_id(id):
    """
    Find a station name and station's info by its id.
    Return: (station_name:str, station_info:dict)
    """
    for name, value in stations.items():
        if value["id"] == id:
            return name, value

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

def set_from_to_staion_id(tps, station_id):
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


def get_train_type(data):
    """
    get train type from img src
    img/rapid.svg
    """
    # get img object by class
    train_type_img = data.select("img.position-item__img")
    # get img src url
    src = train_type_img[0]["src"]
    # parse train type
    src_filename = src.split("/")[-1][:-4]
    train_type = src_filename.replace("_r_position", "")
    return train_type

def get_all_train_element(position_info, all_train_element, train_in):
    # train_in: "on" or "over"
    """
    Parse position info data and store it in all_train_element.

    Args:
        position_info (list): list of position info objects
        all_train_element (dict): dictionary to store parsed data
        train_in (str): either "on" or "over" - indicates whether the train is in or over the station

    Returns:
        all_train_element (dict): parsed all of train's informationdata
    """
    # parse the trains position info
    for station_idx, position_info_item in enumerate(position_info):
        for idx, parent in enumerate(position_info_item):
            # normal case
            # throw out empty element
            if parent.name is None:
                continue
            # set the direction by html structure
            direction = "down" if idx == 0 else "up"
            # set the station id
            station_id = station_idx if direction == "up" else station_idx

            # find the 'train' object
            found_child = parent.select(".position-item__img")
            # throw out empty element
            if not found_child:
                continue
            
            # special case (structure is different)
            # 2_or_more train (-> it happens when there is a lack of space on the website.)
            overchild = None
            for element in found_child:
                if "2_or_more" in element.get("src"):
                    overchild = element

            # add normal train 
            if found_child and station_id != -1:
                for child in found_child:
                    all_train_element[str(station_id)].append({
                        "direction": direction,
                        "train_in": train_in,
                        "data": child.parent,
                    })

            # add special case's child train
            if overchild:
                childs = overchild.select(".position-info__popup .position-item")
                for child in childs:
                    all_train_element[str(station_id)].append({
                    "direction": direction,
                    "train_in": train_in,
                    "data": child.parent,
                })
    return all_train_element

def element_format_train_data(all_train_element):
    """
    Format train data from the given all train elements.
    Parse train data from the given all_train_element.

    Args:
        all_train_element ( dict ): on train data

    Returns:
        train_data ( dict ): formatted train data. Filtered empty element.
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
    for station_id, data in all_train_element.items():
        # throw out empty element
        if not data:
            continue

        for idx, item in enumerate(data):
            # info-1. set the train informations
            train_type = multi_replace(get_train_type(item["data"]), NEW_TRAIN_TYPE)
            train_level = get_train_level(train_type)
            direction = item["direction"]
            
            # info-2.get the train informations
            # function parameters
            tps = {
                "on_station": "1" if item["train_in"] == "on" else "0",
                "direction": "r" if direction == "up" else "l",
                "unknown_value": ""
            }
            station_id = int(station_id)
            # get train info
            from_station_name, to_station_name, from_station_id = set_from_to_staion_id(tps, station_id)
            before_station_name, before_station_id = get_before_station(from_station_id, train_level, direction)
            
            # info-3.parse the contents
            from src.parse.formatting import train_rate_time_formatting, destination_formatting
            destination = item["data"].find(class_=re.compile("to-station")).get_text(strip=True)
            destination = destination_formatting(destination)
            train_rate_time_str = item["data"].find(class_="delay-time").get_text(strip=True)
            train_rate_time_str = train_rate_time_formatting(train_rate_time_str)
            
            # store information
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

def filter_delayed(train_data):
    return {k:v for k,v in train_data.items() if v["train_rate_time_str"]}