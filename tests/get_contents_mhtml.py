from bs4 import BeautifulSoup
import email

def parse_mhtml_to_soup(mhtml_content):
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

rate_info = []
for counting in range(20):
    target = soup.find("div", id = f"unko_joho_shosai_{counting}_naiyo")
    if target is None:
        break
    target_soup = BeautifulSoup(target.prettify(), 'html.parser')
    for tag in target_soup.find_all(["br"]):
        tag.decompose()
    rate_info.append(target_soup)
    
print(rate_info)
print("*"*20)
print(rate_info[0].find("p").text)