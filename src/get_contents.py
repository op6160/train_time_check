from libs import get_html_content, log
from bs4 import BeautifulSoup
import re

# const
go_up_keyword = "【下り線】"
go_down_keyword = "【上り線】"

# text processing
def text_remove_whitespace(text):
    """'Remove whitespace' and 'replace newlines to whitespace' from a string."""
    text = text.replace(" ", "")
    text = text.replace("　", "")
    text = text.replace("\t", "")
    return text.strip()

def text_replace_newlines(text):
    """Replace newlines to whitespace."""
    text = text.replace("\n\n\n\n", " ")
    text = text.replace("\n\n\n", " ")
    text = text.replace("\n\n", " ")
    text = text.replace("\n", " ")
    return text

def text_normalizing_symbol(text):
    """Replace similar symbols to one symbol."""
    text = text.replace("～","~")
    text = text.replace("〜","~")
    text = text.replace("（","(")
    text = text.replace("）",")")
    return text

# list processing
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

def list_processing(soup):
    """
    XXX: hard code
    """
    rate_info = []
    targets = soup.find_all('div', id=re.compile(r'^unko_joho_shosai_\d+_naiyo'))
    targets = len(targets)
    if targets is None:
        raise ValueError("error: targets is None")
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
    return rate_info

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
        log("warn: go_up_info is empty")
        go_up_info.append("")
    if len(go_down_info) == 0:
        log("warn: go_down_info is empty")
        go_down_info.append("")
    return go_down_info, go_up_info

def report_info_check(go_info:list, direction:str):
    """
    Check if there is keyword in the given info list.
    If there is, send email with data.
    """
    report_flag = False
    # set keywords to check (important: it must be opposite of direction and keyword)
    keyword = go_down_keyword if direction == "up" else go_up_keyword
    for info in go_info:
        if keyword in info:
            log(f"error: {keyword} detected in {direction} info: {info}")
            report_flag = True
    if report_flag:
        # Do: send email with data
        # TODO: implement email sending
        pass
    return

def write_state_message(go_info:list, direction:str):
    """
    XXX: hard code. format:
    【下り線】 ~~
    新快速～～行き（～～〇〇時〇〇分）快速～～行き（～～☓☓時☓☓分）
    """
    def it_is_not_taketoyo(message):
        """usecase"""
        return None if "武豊行き" in message else message
    # init
    state_message = ""
    # report check
    report_info_check(go_info, direction)
    # keyword set
    keyword = go_up_keyword if direction == "up" else go_down_keyword
    for idx, info in enumerate(go_info):
        message = text_remove_whitespace(info)
        if idx == 0:
            state_message = message+"\n"
            continue
        message = message.replace(keyword, "").strip()

        # filtering taketoyo line
        message = it_is_not_taketoyo(message)
        if not message:
            continue
        
        # one line one info formatting
        if message.count(")") > 1:
            message = message.replace(")", ")\n")
        else:
            message += "\n"
        state_message += message
    return state_message


BASE_URL = "https://traininfo.jr-central.co.jp/"
url = BASE_URL + "zairaisen/status_detail.html?line=10001"

html = get_html_content(url)
soup = BeautifulSoup(html, 'html.parser')

# get rate_info
rate_info = list_processing(soup)
rate_info = list_sort_by_titile(rate_info)

go_down_info, go_up_info = split_rate_info(rate_info)
go_down_title = go_down_info[0]
go_up_title = go_up_info[0]

print(rate_info)
print(go_down_info)
print(go_up_info)