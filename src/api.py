from src.parse.constants import stationID as stations
from src.get_contents import get_train_rate_and_time_info, write_state_message, print_message

def get_train_status_api(language="ko", direction=None):
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

def get_train_status_range_api(station, range_n=6, language="ko", direction=None):
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

if __name__ == "__main__":
    # Test Code (CLI usage)
    result = get_train_status_range_api("刈谷", range_n=6, language="ko", direction="up")
    # result = get_train_status_api(language="ko", direction="up")
    
    if result["status"] == "normal":
        print(result["message"])
        print(result["data"])
    else:
        print_message(result["notice_message"], result["train_messages"])