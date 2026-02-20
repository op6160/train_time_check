from src.libs import get_html_content, logger
from bs4 import BeautifulSoup
import re
from config import (
    go_up_keyword,
    go_down_keyword,
    fine_keyword,
    BASE_URL,
    STATE_URL,
)
from src.parse.train_info import get_train_info
from src.parse.parse_util import (
    re_form,
    text_remove_whitespace,
    text_replace_newlines,
    text_normalizing_symbol,
    soup_find_all_div_by_id
)

def get_train_rate_and_time_info():
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
    def get_driving_state(soup):
        """
        XXX: hard code
        """
        rate_info = []
        targets = soup.find_all('div', id=re.compile(r'^unko_joho_shosai_\d+_naiyo'))
        targets = len(targets)
        if targets is None:
            raise ValueError("error: targets is None")

        # get train driving state
        state_title = soup.find("p", "shosai-bun").text
        if state_title is None:
            raise ValueError("error: state_title is None")
        elif fine_keyword == state_title:
            # driving state is fine
            state_train = True
        else:
            state_train = False

        if not state_train:
            for counting in range(targets):
                # get info div
                rate_info_div = soup.find("div", id = f"unko_joho_shosai_{counting}_naiyo")
                if rate_info_div is None:
                    break
                # div to soup to get text
                rate_info_div_soup = BeautifulSoup(rate_info_div.prettify(), 'html.parser')
                # remove </br>
                for tag in rate_info_div_soup.find_all(["br"]):
                    tag.decompose()
                # get text
                rate_info_div_soup_text = rate_info_div_soup.find("p").text
                # normalize the text
                rate_info_div_soup_text = text_remove_whitespace(rate_info_div_soup_text)
                rate_info_div_soup_text = text_replace_newlines(rate_info_div_soup_text)
                rate_info_div_soup_text = text_normalizing_symbol(rate_info_div_soup_text)
                # append to list
                rate_info.append(rate_info_div_soup_text)
        return {
            "rate_info": rate_info,
            "driving_state_train": state_train,
            "driving_state_title": state_title
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


    # get html
    url = BASE_URL + STATE_URL
    html = get_html_content(url = url, load_time = 3)
    soup = BeautifulSoup(html, 'html.parser')

    # get notice
    train_state_data = get_driving_state(soup)
    state_train = train_state_data["driving_state_train"]
    state_title = train_state_data["driving_state_title"]
    rate_info = train_state_data["rate_info"]

    if state_train:
        return state_train, state_title, None

    rate_info = list_sort_by_titile(rate_info)
    notice_data = notice_data_packing(rate_info)

    # get rate train times
    rate_time_soup_find = soup_find_all_div_by_id(soup, re_form("okure-jikan-ja", ""))
    train_data = {}

    for idx, data in enumerate(rate_time_soup_find):
        if data.text:
            train_info_info = get_train_info(data)
            train_data[str(idx)] = train_info_info
    return state_train, notice_data, train_data