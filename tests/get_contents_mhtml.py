from bs4 import BeautifulSoup

# ======================================================================================= #
import email
def parse_mhtml_to_soup(mhtml_content):
    """tester code"""
    msg = email.message_from_string(mhtml_content)
    html_content = None
    # find text/html
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            # decode
            html_content = part.get_payload(decode=True)
            charset = part.get_content_charset()
            if charset:
                html_content = html_content.decode(charset, errors='replace')
            break
    
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup
    else:
        return None

with open("tests/dev.test.mhtml", 'r', encoding='utf-8') as f:
    mhtml_text = f.read()
    soup = parse_mhtml_to_soup(mhtml_text)
# ======================================================================================= #

def text_squash(text):
    """'Remove whitespace' and 'replace newlines to whitespace' from a string."""
    text = text.replace(" ", "")
    text = text.replace("\t", "")
    text = text.replace("\n\n", " ")
    text = text.replace("\n", " ")
    return text.strip()

def hard_coding_logic(rate_info):
    result = []
    for info in rate_info:
        if info[0] == "【":
            result.append(info)
        else:
            result[-1] += info
    return result

rate_info = []
for counting in range(20):
    rate_info_div = soup.find("div", id = f"unko_joho_shosai_{counting}_naiyo")
    if rate_info_div is None:
        break
    rate_info_div_soup = BeautifulSoup(rate_info_div.prettify(), 'html.parser')
    for tag in rate_info_div_soup.find_all(["br"]):
        tag.decompose()
    rate_info_div_soup_text = rate_info_div_soup.find("p").text
    rate_info_div_soup_text = text_squash(rate_info_div_soup_text)
    rate_info.append(rate_info_div_soup_text)
    rate_info = hard_coding_logic(rate_info)

# print(rate_info)
print("*"*20)
print("rate_info: ")
for rate in rate_info:
    print(rate)
# print(rate_info[0]) # .find("p").text
print("*"*20)
