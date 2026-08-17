from src.constants.station_map import stationID as stations
from src.model.model import TrainDataModel, TrainDirectionMappingModel
from src.parse.formatting import train_rate_time_formatting, destination_formatting

import os
import sys

import re
from src.parse.parse_util import multi_replace
from src.constants.station_map import NEW_TRAIN_TYPE

from src.libs import logger

stations_by_id = {info["id"]: (name, info) for name, info in stations.items()}

def find_station_by_id(id):
    """
    Find a station name and station's info by its id.
    Return: (station_name:str, station_info:dict)
    """
    return stations_by_id.get(id, (None, None))

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

def set_before_to_staion_id(tps, station_id):
        """
        Set before_passed_station_id and to_station_id based on the given train params.

        Args:
            tps ( TrainDirectionMappingModel ): train params

        Returns:
            before_passed_station ( str ): before station name
            to_station ( str ): to station name
            before_passed_station_id ( int ): before station id to use in get_before_station
        """
        down_on_station_case = tps.on_station == "1"  and tps.direction == "l"
        down_not_on_station_case = tps.on_station == "0" and tps.direction == "l"
        up_case = tps.direction == "r"

        if down_on_station_case:
            before_passed_station_id = station_id + 1
            to_station_id = station_id
        elif down_not_on_station_case:
            before_passed_station_id = station_id
            to_station_id = station_id - 1
        elif up_case:
            before_passed_station_id = station_id
            to_station_id = station_id + 1
        else:
            raise Exception("Invalid train params")
        before_passed_station, ___ = find_station_by_id(before_passed_station_id)
        to_station, ___ = find_station_by_id(to_station_id)

        return before_passed_station, to_station, before_passed_station_id , to_station_id 

def get_before_station(current_before_id, train_level, direction):
        """
        Find a before stop station name by train,station level.
        """
        # XXX: 데이터 구조를 잘못 설계해서, idx기반으로 구현했음
        values = list(stations.values())
        if direction == "up":
            if values[current_before_id]["level"] < train_level: #역의 레벨이 기차레벨보다 낮을 때
                return get_before_station(current_before_id - 1, train_level, direction)
        elif direction == "down":
            if values[current_before_id]["level"] < train_level:
                return get_before_station(current_before_id + 1, train_level, direction)
        keys = list(stations.keys())
        station_name = keys[current_before_id]
        station_id = str(stations[station_name]["id"])
        return station_name, station_id

def get_next_station(current_to_id, train_level, direction):
        """
        Find a next stop station name by train,station level.
        """
        # XXX: 데이터 구조를 잘못 설계해서, idx기반으로 구현했음
        values = list(stations.values())
        if direction == "up":
            if values[current_to_id]["level"] < train_level: #역의 레벨이 기차레벨보다 낮을 때
                return get_next_station(current_to_id + 1, train_level, direction)
        elif direction == "down":
            if values[current_to_id]["level"] < train_level:
                return get_next_station(current_to_id - 1, train_level, direction)
        keys = list(stations.keys())
        station_name = keys[current_to_id]
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
        station_id = str(station_idx)
        dir_containers = []

        if train_in == "on":
            # position-info-header: 1st container is left track (down), 2nd container is right track (up)
            containers = position_info_item.find_all("div", class_="position-info-header__position-items")
            if len(containers) >= 1:
                dir_containers.append(("down", containers[0]))
            if len(containers) >= 2:
                dir_containers.append(("up", containers[1]))
        else:
            # position-info-contents: left track is down, right track is up
            left = position_info_item.find("div", class_="position-info__left")
            right = position_info_item.find("div", class_="position-info__right")
            if left:
                dir_containers.append(("down", left))
            if right:
                dir_containers.append(("up", right))

        for direction, container in dir_containers:
            for p_item in container.find_all("div", class_="position-item"):
                img = p_item.find("img", class_="position-item__img")
                if not img:
                    continue

                # 2_or_more train case
                if "2_or_more" in img.get("src", ""):
                    popup_items = p_item.select(".position-info__popup .position-item")
                    if popup_items:
                        for child in popup_items:
                            if child.find("img", class_="position-item__img"):
                                all_train_element[station_id].append({
                                    "direction": direction,
                                    "train_in": train_in,
                                    "data": child,
                                })
                else:
                    all_train_element[station_id].append({
                        "direction": direction,
                        "train_in": train_in,
                        "data": p_item,
                    })

    return all_train_element

def element_format_train_data(all_train_element):
    """
    Format train data from the given all train elements.
    Parse train data from the given all_train_element.

    Args:
        all_train_element ( dict ): on train data

    Returns:
        train_data_list ( list[TrainDataModel] ): formatted train data. Filtered empty element.
    """
    train_data_list = []
    for station_id, data in all_train_element.items():
        # throw out empty element
        if not data:
            continue

        station_id = int(station_id)

        for idx, item in enumerate(data):
            # info-1. set the train informations
            train_type = multi_replace(get_train_type(item["data"]), NEW_TRAIN_TYPE)
            train_level = get_train_level(train_type)
            
            direction = item["direction"]
            on_station = item["train_in"]

            # info-2.get the train informations
            # function parameters, it was used in before system.
            tps = TrainDirectionMappingModel(
                on_station=item["train_in"],
                direction=direction
            )

            # get train info
            before_passed_station, to_station, before_passed_station_id, to_station_id = set_before_to_staion_id(tps, station_id)
            arrived_station, before_station_id = get_before_station(before_passed_station_id, train_level, direction)
            next_stop, next_station_id = get_next_station(to_station_id, train_level, direction)

            # info-3.parse the contents
            dest_tag = item["data"].find(class_=re.compile("to-station"))
            destination = dest_tag.get_text(strip=True) if dest_tag else ""
            destination = destination_formatting(destination)
            
            delay_tag = item["data"].find(class_="delay-time")
            train_rate_time_str = delay_tag.get_text(strip=True) if delay_tag else ""
            train_rate_time_str = train_rate_time_formatting(train_rate_time_str)
            
            # store information
            train_data = TrainDataModel(
                id=station_id,
                train_type=train_type,
                train_level=train_level,
                direction=direction,
                destination=destination,
                before_passed_station=before_passed_station,
                to_station=to_station,
                train_rate_time_str=train_rate_time_str,
                arrived_station=arrived_station,
                before_station_id=before_station_id,
                next_stop=next_stop,
                next_station_id=next_station_id,
            )
            train_data_list.append(train_data)            
    return train_data_list

def filter_delayed(train_data_list:list):
    result = []
    for train_data in train_data_list:
        if train_data.train_rate_time_str:
            result.append(train_data)
    return result