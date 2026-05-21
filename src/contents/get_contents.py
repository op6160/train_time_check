from src.parse.rate_train_info import get_train_rate_and_time_info
from src.constants.station_map import stationID as stations
from src.contents.message import write_state_message

from src.model.model import TrainStatusModel

NO_MESSAGE = None # No message.

# use
def get_train_status(language="ko", direction=None) -> TrainStatusModel:
    """
    API Entry point to get train status.
    
    Args:
        language (str): 'ko', 'en', 'ja' (user might say 'jp' but code uses 'ja')
        direction (str): 'up', 'down', or None

    Returns:
        TrainStatusModel: Structured response containing status and messages.
    """
    # Normalize language code if necessary (e.g., jp -> ja)
    if language == "jp": language = "ja"

    is_train_state_normal, notice_data, train_data_list = get_train_rate_and_time_info()
    
    if is_train_state_normal:
        # All trains are operating normally (no delay data)
        return TrainStatusModel(
            status="normal",
            status_message="All trains are operating normally. No notification sent.",
            notice_message=NO_MESSAGE,
            train_message=NO_MESSAGE,
            notice_data=notice_data,
            raw_data=train_data_list
        )
    else:
        notice_message, train_message = write_state_message(language, train_data_list, notice_data, direction)
        return TrainStatusModel(
            status="delay",
            status_message="Some trains are delayed.",
            notice_message=notice_message,
            train_message=train_message,
            notice_data=notice_data,
            raw_data=train_data_list
        )

def get_train_status_range(station, range_n=6, language="ko", direction=None) -> TrainStatusModel:
    """
    API Entry point to get train status filtered by target station and range.
    
    Args:
        station (str): Target station name (e.g., "刈谷")
        range_n (int): Range buffer (+- n stations)
        language (str): 'ko', 'en', 'ja'
        direction (str): 'up', 'down', or None

    Returns:
        TrainStatusModel: Structured response containing status and messages.
    """
    def get_station_id(name):
        return stations[name]["id"] if name in stations else None

    # Normalize language
    if language == "jp": language = "ja"

    is_train_state_normal, notice_data, train_data_list = get_train_rate_and_time_info()

    if is_train_state_normal:
        # All trains are operating normally (no delay data)
        return TrainStatusModel(
            status="normal",
            status_message="All trains are operating normally. No notification sent.",
            notice_message=NO_MESSAGE,
            train_message=NO_MESSAGE,
            notice_data=notice_data,
            raw_data=train_data_list
        )
        
    # Filter logic
    target_id = get_station_id(station)
    
    if target_id is not None and direction:
        filtered_data_list = []
        for train_data in train_data_list:
            # 1. Check direction
            if train_data.direction != direction:
                continue
                
            current_id = get_station_id(train_data.arrived_station)
            if current_id is None:
                continue
            # 2. Check range based on direction
            # 'up' in this code means ID increasing (Toyohashi -> Maibara)
            if direction == "up":
                if target_id - range_n <= current_id <= target_id:
                    filtered_data_list.append(train_data)
            elif direction == "down":
                if target_id <= current_id <= target_id + range_n:
                    filtered_data_list.append(train_data)

    notice_message, train_message = write_state_message(language, filtered_data_list, notice_data, direction)
    return TrainStatusModel(
        status="delay",
        status_message="Some trains are delayed.",
        notice_message=notice_message,
        train_message=train_message,
        notice_data=notice_data,
        raw_data=filtered_data_list
    )