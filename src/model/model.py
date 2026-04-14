from dataclasses import dataclass

# @dataclass
# class MessageDataModel:
#     notice_message: str
#     train_messages: list

@dataclass
class TrainDataModel:
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
    go_down_title: str
    go_down_info: list
    go_up_title: str
    go_up_info: list
    _rate_info: list
    state_title: str

@dataclass
class TrainDirectionMappingModel:
    on_station: str
    direction: str

    def __post_init__(self):
        self.on_station = "1" if self.on_station == "on" else "0"
        self.direction = "r" if self.direction == "up" else "l"

@dataclass
class MessageDataModel:
    is_train_state_normal: bool
    notice_data: NoticeDataModel
    train_data_list: list[TrainDataModel]


@dataclass
class TrainStatusModel:
    status: str #
    status_message: str #
    notice_message: str #
    train_message: str #
    notice_data: NoticeDataModel #
    raw_data: list[TrainDataModel]