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