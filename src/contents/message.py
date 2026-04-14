# typing
from src.model.model import TrainDataModel, NoticeDataModel
import re

def gen_train_info_message(train_data: TrainDataModel, message_form: dict) -> str:
    """
    Generate message from train info and given language format.

    Args:
        train_data (TrainDataModel): Train info.
        message_form (dict): Language format.

    Returns:
        str: Generated message.
    """
    # 1. read train info
    train_type = train_data.train_type
    direction = train_data.direction
    destination = train_data.destination
    how_long = train_data.train_rate_time_str
    arrived_station = train_data.arrived_station
    before_passed_station = train_data.before_passed_station
    to_station = train_data.to_station                       # next_station
    next_stop = train_data.next_stop                         # next_stop_station

    # 2. read language format
    going = message_form["destination"]
    delayed = message_form["rate_time"]
    from_ = message_form["from_station"]
    via_ = message_form["before_station"]
    to_ = message_form["to_station"]
    arrive_soon = message_form["arrive_soon"]

    # read for caculate data
    train_level = train_data.train_level

    # 3. write message
    # first line: train type and delay time
    message = f'[{train_type}][{direction} {destination}{going}] {how_long}{delayed}\n'
    
    # second line: arrived_station -> next_stop_station
    message += f"🟢{arrived_station} → 🛑{next_stop}" + " "
    
    if train_level == 0:
        # normal train 
        pass    
    else:
        # rapid train: second line - details
        message += "["
        if not arrived_station == before_passed_station:
            # station info: before passed station 
            message += f"{before_passed_station}{via_}" 
        if to_station == next_stop:
            # arrival message
            message += f"{arrive_soon}" 
        else:
            # station info: next stop station
            message += f"{to_station}{to_}"
        message += "]"

    # format message
    message = message.replace("以上","+")
    return message

from src.constants.language_map import en_form, ko_form, ja_form
def set_language_form(language):
    if language == "en":
        return en_form()
    elif language == "ko":
        return ko_form()
    elif language == "ja":
        return ja_form()
    else:
        raise ValueError("error: language is not supported")

from src.constants.language_map import dict_replace
def write_state_message(language, train_data_list, notice_data, direction=None):
    """
    Write state message in the given language.

    Args:
        language (str): the language to write in.
        train_data_list (list): the train data to write.
        notice_data (NoticeDataModel): the notice data to write.
        direction ("up" or "down", optional): the direction to write. If not given, write all data. 
    """

    message_form, replace_map = set_language_form(language)

    notice_message = "* notice:"
    train_message = []
    
    # TODO: notice message is not translated
    if direction in ("up", "down"):
        direction_title = getattr(notice_data, f"go_{direction}_title", "")
        direction_info = getattr(notice_data, f"go_{direction}_info", "")
        notice_message += f"{direction_title}" if direction_title else ""
        notice_message += "\n" if direction_title and direction_info else ""
        notice_message += f"{direction_info}" if direction_info else ""

        for train_data in train_data_list:
            if train_data.direction == direction:
                # display_info = dict_replace(train_data, replace_map)
                new_train_message = gen_train_info_message(train_data, message_form)
                train_message.append(new_train_message)

    else:
        for msg in vars(notice_data).values():
            notice_message += f"{msg}" if msg else ""
        for train_data in train_data_list:
            if train_data.direction == "up" or train_data.direction == "down":
                # display_info = dict_replace(train_data, replace_map)
                new_train_message = gen_train_info_message(train_data, message_form)
                train_message.append(new_train_message)
    
    # 키를 길이의 내림차순으로 정렬: "西岡崎"가 "岡崎"보다 빠르게 처리되도록 함
    # re 성능 최적화
    sorted_keys = sorted(replace_map.keys(), key=len, reverse=True)
    pattern = re.compile("|".join(map(re.escape, sorted_keys)))
    translated_train_message = [pattern.sub(lambda m: replace_map[m.group(0)], message) for message in train_message]
    train_message = translated_train_message

    if notice_message == "* notice:": notice_message = ""
    return notice_message, train_message