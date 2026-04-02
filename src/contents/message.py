def gen_train_info_message(info: dict, message_form: dict) -> str:
    """
    Generate message from train info and given language format.

    Args:
        info (dict): Train info.
        message_form (dict): Language format.

    Returns:
        str: Generated message.
    """
    # 1. read train info
    train_type = info["train_type"]
    direction = info["direction"]
    destination = info["destination"]
    how_long = info["train_rate_time_str"]
    # from_station = info["from_station_name"] # it was changed
    # via_station = info["before_station_name"] # it was changed
    arrived_station = info["arrived_station"]             # arrived_station
    before_passed_station = info["before_passed_station"] # before_passed_station
    to_station = info["to_station"]                       # next_station
    next_stop = info["next_stop"]                         # next_stop_station

    # 2. read language format
    going = message_form["destination"]
    delayed = message_form["rate_time"]
    from_ = message_form["from_station"]
    via_ = message_form["before_station"]
    to_ = message_form["to_station"]
    arrive_soon = message_form["arrive_soon"]

    # 3. write message
    # first line: train type and delay time
    message = f'[{train_type}][{direction} {destination}{going}] {how_long}{delayed}\n'
    
    # second line: arrived_station -> next_stop_station
    message += f"🟢{arrived_station} → 🛑{next_stop}" + " "
    
    # second line: details
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
def write_state_message(language, train_data, notice_data, direction=None):
    """
    Write state message in the given language.

    Args:
        language (str): the language to write in.
        train_data (dict): the train data to write.
        notice_data (dict): the notice data to write.
        direction ("up" or "down", optional): the direction to write. If not given, write all data. 
    """

    message_form, replace_map = set_language_form(language)

    notice_message = "* notice:"
    train_message = []

    # TODO: notice message is not translated
    if direction in ("up", "down"):
        direction_title = notice_data.get(f"go_{direction}_title", "")
        direction_info = notice_data.get(f"go_{direction}_info", "")
        notice_message += f"{direction_title}" if direction_title else ""
        notice_message += "\n" if direction_title and direction_info else ""
        notice_message += f"{direction_info}" if direction_info else ""

        for info in train_data.values():
            if info["direction"] == direction:
                display_info = dict_replace(info, replace_map)
                new_train_message = gen_train_info_message(display_info, message_form)
                train_message.append(new_train_message)

    else:
        for msg in notice_data.values():
            notice_message += f"{msg}" if msg else ""
        for info in train_data.values():
            if info["direction"] == "up":
                display_info = dict_replace(info, replace_map)
                new_train_message = gen_train_info_message(display_info, message_form)
                train_message.append(new_train_message)

        for info in train_data.values():
            if info["direction"] == "down":
                display_info = dict_replace(info, replace_map)
                new_train_message = gen_train_info_message(display_info, message_form)
                train_message.append(new_train_message)

    if notice_message == "* notice:": notice_message = ""
    return notice_message, train_message