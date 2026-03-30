from src.libs import logger
from bs4 import BeautifulSoup # for typing

from config import (
    BASE_URL,
    STATE_URL,
    MESSAGE_URL,
)

# soup util
from src.utility import get_soup_by_url

# train info
from src.parse.train_info import (
    get_all_train_element, 
    element_format_train_data, 
    filter_delayed
)

# notice info
from src.parse.notice_info import (
    get_driving_state, 
    notice_data_packing, 
    list_sort_by_titile
)
    
def get_train_rate_and_time_info() -> tuple[bool, dict, dict]:
    """
    Get train rate and time information from the given html source.

    Returns:
        notice_data ( dict ): notice data
            {
                "go_down_title":str, 
                "go_down_info":list, 
                "go_up_title":str, 
                "go_up_info":list, 
                "_rate_info":list
            }
        train_data ( dict ): train data
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
    soup = get_soup_by_url(BASE_URL + STATE_URL)
    message_soup = get_soup_by_url(BASE_URL + MESSAGE_URL)

    # notice data parse
    # __state_train is the remnant of the previous version. 
    # it replaced 'not delayed_train_data'.
    __state_train, notice_data, state_title = notice_data_flow(message_soup)
    delayed_train_data = train_data_flow(soup)
    state_train = not delayed_train_data  # == {}

    if not state_train:
        # has delay data
        delayed_train_data = train_data_flow(soup)
    else:
        # no delay data
        notice_data = {"state_title": state_title} # state_tilte is webhook message title, in this case, other notice_data is empty.
    return state_train, notice_data, delayed_train_data
        

def notice_data_flow(soup: BeautifulSoup) -> tuple[bool, dict, str]:
    """
    Parse notice data from the soup.

    Returns:
        state_train ( bool ): train state
        notice_data ( dict ): notice data
            {
                "go_down_title":str, 
                "go_down_info":list, 
                "go_up_title":str, 
                "go_up_info":list, 
                "_rate_info":list
            }
        state_title ( str ): webhook message title
    """
    train_state_data = get_driving_state(soup)
    # train state
    state_train = train_state_data["driving_state_train"]
    # webhook message title
    state_title = train_state_data["driving_state_title"]
    
    # no delay data
    if state_train:
        return state_train, {}, state_title
    
    # get notice data
    delay_info = train_state_data["rate_info"]
    # processing
    delay_info = list_sort_by_titile(delay_info)
    notice_data = notice_data_packing(delay_info)
    return state_train, notice_data, state_title

def train_data_flow(soup: BeautifulSoup) -> dict:
    """
    Parse train data from the given soup object.

    Args:
        soup ( BeautifulSoup ): Soup object

    Returns:
        train_data ( dict ): train data
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
    # find the station elements in the soup
    on_station_elements = soup.find_all("div", class_ = "position-info-header")
    over_station_elements = soup.find_all("div", class_ = "position-info-contents")
    station_count = len(on_station_elements)

    # initialize the elements
    all_train_element = {
        str(idx): []
        for idx in range(station_count)
    }

    # find the train elements from station elements.
    all_train_element = get_all_train_element(on_station_elements, all_train_element, "on")
    all_train_element = get_all_train_element(over_station_elements, all_train_element, "over")

    # parse the train elements
    train_data = element_format_train_data(all_train_element)
    delayed_train_data = filter_delayed(train_data)
    return delayed_train_data