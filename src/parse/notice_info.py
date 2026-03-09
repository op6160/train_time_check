import re
from src.libs import logger

def get_driving_state(soup):
    """
    TODO: this function should be refactored.
    Get train driving state from the given new source. train_information.html
    """
    
    rate_info = []
    targets = soup.find("p", class_=re.compile("status-text"))
    if targets.text.strip() == "平常運転":
        driving_state_train = True
    else:
        driving_state_train = False
    driving_state_title = targets.text
    
    return {
        "rate_info": rate_info,
        "driving_state_train": driving_state_train,
        "driving_state_title": driving_state_title,
    }

def notice_data_packing(rate_info):
    def split_rate_info(rate_info):
        """
        XXX: hard code
        Split rate info by keyword.
        """
        # init
        go_down_info = [] # morning
        go_up_info = [] # night

        # split
        for rate in rate_info:
            if go_up_keyword in rate:
                go_up_info.append(rate)

                if go_down_keyword in rate:
                    if rate.find(go_up_keyword) > rate.find(go_down_keyword):
                        go_up_info[-1] = rate[rate.find(go_up_keyword):].strip()
                    else:
                        go_up_info[-1] = rate[rate.find(go_up_keyword):rate.find(go_down_keyword)].strip()

            if go_down_keyword in rate:
                go_down_info.append(rate)

                if go_up_keyword in rate:
                    if rate.find(go_up_keyword) < rate.find(go_down_keyword):
                        go_down_info[-1] = rate[rate.find(go_down_keyword):].strip()
                    else:
                        go_down_info[-1] = rate[rate.find(go_down_keyword):rate.find(go_up_keyword)].strip()
        
        # add empty string to avoid go_up_title and go_down_title allocating error
        if len(go_up_info) == 0:
            logger.info("go_up_info is empty")
            go_up_info.append("")
        if len(go_down_info) == 0:
            logger.info("go_down_info is empty")
            go_down_info.append("")
        return go_down_info, go_up_info

    go_down_info, go_up_info = split_rate_info(rate_info)

    go_down_title = go_down_info[0]
    go_up_title = go_up_info[0]
    go_down_info = go_down_info[1:]
    go_up_info = go_up_info[1:]

    notice_data = {
    "go_down_title": go_down_title,
    "go_down_info": go_down_info,
    "go_up_title": go_up_title,
    "go_up_info": go_up_info,
    "_rate_info": rate_info
    }
    return notice_data
def list_sort_by_titile(rate_info):
    """
    XXX: hard code.
    Sort rate info by title.

    Take a list of rate info and sort it by title.
    If the info starts with "【", it is considered as a title.
    Otherwise, it is considered as contents of the previous title.
    """
    result = []
    for info in rate_info:
        if info.startswith("【"):
            result.append(info)
        else:
            result[-1] += info
    return result