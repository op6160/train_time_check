from src.parse.rate_train_info import get_train_rate_and_time_info
from src.parse.station_map import stationID as stations
from src.language_map import en_form, ko_form, ja_form, dict_replace

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
        # read data
        train_type = info["train_type"]
        direction = info["direction"]
        destination = info["destination"]
        how_long = info["train_rate_time_str"]
        from_station = info["from_station_name"]
        via_station = info["before_station_name"]
        to_station = info["to_station_name"]

        going = message_form["destination"]
        delayed = message_form["rate_time"]
        from_ = message_form["from_station"]
        via_ = message_form["before_station"]
        to_ = message_form["to_station"]

        # write message
        # 1st line: train type and delay time
        message = f'[{train_type}][{direction} {destination}{going}] {how_long}{delayed}\n'
        # 2nd line: from station (-> before station) -> to station
        if from_station == via_station:
            message += f'"{from_station}"{from_}"{to_station}"{to_}'
        else:
            message += f'"{from_station}"{from_}"{via_station}"{via_}"{to_station}"{to_}'

        # format message
        message = message.replace("以上","+")
        return message

    def set_language_form(language):
        if language == "en":
            return en_form()
        elif language == "ko":
            return ko_form()
        elif language == "ja":
            return ja_form()
        else:
            raise ValueError("error: language is not supported")

    message_form, replace_map = set_language_form(language)

    notice_message = "* notice:"
    train_message = []

    # TODO: notice message is not translated
    if direction in ("up", "down"):
        direction_title = f"go_{direction}_title"
        direction_info = f"go_{direction}_info"
        notice_message += f"{notice_data[direction_title]}" if notice_data[direction_title] else ""
        notice_message += "\n" if notice_data[direction_title] and notice_data[direction_info] else ""
        notice_message += f"{notice_data[direction_info]}" if notice_data[direction_info] else ""

        for info in train_data.values():
            if info["direction"] == direction:
                display_info = dict_replace(info, replace_map)
                new_train_message = gen_message(display_info, message_form)
                train_message.append(new_train_message)

    else:
        for msg in notice_data.values():
            notice_message += f"{msg}" if msg else ""
        for info in train_data.values():
            if info["direction"] == "up":
                display_info = dict_replace(info, replace_map)
                new_train_message = gen_message(display_info, message_form)
                train_message.append(new_train_message)

        for info in train_data.values():
            if info["direction"] == "down":
                display_info = dict_replace(info, replace_map)
                new_train_message = gen_message(display_info, message_form)
                train_message.append(new_train_message)

    if notice_message == "* notice:": notice_message = ""
    return notice_message, train_message

# use
def get_train_status(language="ko", direction=None):
    """
    API Entry point to get train status.
    
    Args:
        language (str): 'ko', 'en', 'ja' (user might say 'jp' but code uses 'ja')
        direction (str): 'up', 'down', or None

    Returns:
        dict: Structured response containing status and messages.
    """
    # Normalize language code if necessary (e.g., jp -> ja)
    if language == "jp": language = "ja"

    state_train, notice_data, train_data = get_train_rate_and_time_info()
    
    if state_train:
        return {
            "status": "normal",
            "message": "All trains are operating normally.",
            "data": notice_data
        }
    else:
        notice_message, train_message = write_state_message(language, train_data, notice_data, direction)
        return {
            "status": "delay",
            "notice_message": notice_message,
            "train_messages": train_message,
            "raw_data": train_data
        }

def get_train_status_range(station, range_n=6, language="ko", direction=None):
    """
    API Entry point to get train status filtered by target station and range.
    
    Args:
        station (str): Target station name (e.g., "刈谷")
        range_n (int): Range buffer (+- n stations)
        language (str): 'ko', 'en', 'ja'
        direction (str): 'up', 'down', or None

    Returns:
        dict: Structured response with filtered train info.
    """
    def get_station_id(name):
        return stations[name]["id"] if name in stations else None

    # Normalize language
    if language == "jp": language = "ja"

    state_train, notice_data, train_data = get_train_rate_and_time_info()

    if state_train:
        return {
            "status": "normal",
            "message": "All trains are operating normally.",
            "data": notice_data
        }
    
    # Filter logic
    target_id = get_station_id(station)
    
    if target_id is not None and direction:
        filtered_data = {}
        for k, v in train_data.items():
            # 1. Check direction
            if v["direction"] != direction:
                continue
            
            current_id = get_station_id(v["from_station_name"])
            if current_id is None:
                continue

            # 2. Check range based on direction
            # 'up' in this code means ID increasing (Toyohashi -> Maibara)
            if direction == "up":
                if target_id - range_n <= current_id <= target_id:
                    filtered_data[k] = v
            # 'down' in this code means ID decreasing (Maibara -> Toyohashi)
            elif direction == "down":
                if target_id <= current_id <= target_id + range_n:
                    filtered_data[k] = v
        
        train_data = filtered_data

    notice_message, train_message = write_state_message(language, train_data, notice_data, direction)
    return {
        "status": "delay",
        "notice_message": notice_message,
        "train_messages": train_message,
        "raw_data": train_data
    }

def print_message(notice_message, train_message):
    print("*" * 20)
    print(notice_message)
    print("*" * 20)
    for message in train_message:
        print(message)
    print("*" * 20)

if __name__ == "__main__":
    # Test Code (CLI usage)
    result = get_train_status_range("刈谷", range_n=6, language="ko", direction="up")
    # result = get_train_status(language="ko", direction="up")
    
    if result["status"] == "normal":
        print(result["message"])
        print(result["data"])
    else:
        print_message(result["notice_message"], result["train_messages"])