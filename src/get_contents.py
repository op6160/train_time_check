from src.parse.rate_train_info import get_train_rate_and_time_info
from src.constants import en_form, dict_replace

en_form()

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
        if message_form["lang_type"] != "ja":
            message = message.replace("以上","+")
        return message

    def set_language_form(language):
        if language == "en":
            from constants import en_form
            return en_form()
        elif language == "ko":
            from constants import ko_form
            return ko_form()
        elif language == "ja":
            from constants import ja_form
            return ja_form()
        else:
            raise ValueError("error: language is not supported")

    message_form, replace_map = set_language_form(language)
    from constants import dict_replace

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
                train_message.append(gen_message(display_info, message_form))

    else:
        for msg in notice_data.values():
            notice_message += f"{msg}" if msg else ""
        for info in train_data.values():
            if info["direction"] == "up":
                display_info = dict_replace(info, replace_map)
                train_message.append(gen_message(display_info, message_form))
        for info in train_data.values():
            if info["direction"] == "down":
                display_info = dict_replace(info, replace_map)
                train_message.append(gen_message(display_info, message_form))

    if notice_message == "* notice:": notice_message = ""
    return notice_message, train_message

def print_message(notice_message, train_message):
    print("*" * 20)
    print(notice_message)
    print("*" * 20)
    for message in train_message:
        print(message)
    print("*" * 20)