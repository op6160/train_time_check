from dataclasses import dataclass

# @dataclass
# class MessageDataModel:
#     notice_message: str
#     train_messages: list

@dataclass
class TrainDataModel:
    """_summary_
    Train data model.
    Args:
        id ( str): train id
        train_type ( str): train type
        train_level ( int): train level
        direction ( str): train direction
        destination ( str): train destination
        before_passed_station ( str): before passed station
        to_station ( str): to station
        train_rate_time_str ( str): train rate time string
        arrived_station ( str): arrived station
        before_station_id ( str): before station id
        next_stop ( str): next stop
        next_station_id ( str): next station id
    """
    id: str
    train_type: str
    train_level: int
    direction: str
    destination: str
    before_passed_station: str
    to_station: str
    train_rate_time_str: str
    arrived_station: str
    before_station_id: str
    next_stop: str
    next_station_id: str

@dataclass
class NoticeDataModel:
    """_summary_
    Notice data model.
    Args:
        go_down_title ( str): go down title
        go_down_info ( list): go down info
        go_up_title ( str): go up title
        go_up_info ( list): go up info
        _rate_info ( list): rate info
        state_title ( str): state title
    """
    go_down_title: str
    go_down_info: list
    go_up_title: str
    go_up_info: list
    _rate_info: list
    state_title: str

@dataclass
class TrainDirectionMappingModel:
    """_summary_
    Train direction mapping model.
    Args:
        on_station ( str): on station. If "on": train is on station. -> "1". If "off": train is not on station. -> "0"
        direction ( str): direction. If "up": train is going up. -> "r". If "down": train is going down. -> "l"
    """
    on_station: str
    direction: str

    def __post_init__(self):
        self.on_station = "1" if self.on_station == "on" else "0"
        self.direction = "r" if self.direction == "up" else "l"

@dataclass
class MessageDataModel:
    """_summary_
    Message data model.
    Args:
        is_train_state_normal ( bool): is train state normal
        notice_data ( NoticeDataModel): notice data
        train_data_list ( list[TrainDataModel]): train data list
    """
    is_train_state_normal: bool
    notice_data: NoticeDataModel
    train_data_list: list[TrainDataModel]


@dataclass
class TrainStatusModel:
    """_summary_
    Train status model.
    Args:
        status ( str): train status
        status_message ( str): train status message
        notice_message ( str): notice message
        train_message ( str): train message
        notice_data ( NoticeDataModel): notice data
        raw_data ( list[TrainDataModel]): raw train data list
    """
    status: str #
    status_message: str #
    notice_message: str #
    train_message: str #
    notice_data: NoticeDataModel #
    raw_data: list[TrainDataModel]