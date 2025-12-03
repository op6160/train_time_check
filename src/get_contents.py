from libs import get_html_content
from bs4 import BeautifulSoup

BASE_URL = "https://traininfo.jr-central.co.jp/"
url = BASE_URL + "zairaisen/status_detail.html?line=10001"

html = get_html_content(url)
soup = BeautifulSoup(html, 'html.parser')

rate_info = []
for counting in range(20):
    target = soup.find("div", id = f"unko_joho_shosai_{counting}_naiyo")
    if target is None:
        break
    target_soup = BeautifulSoup(target.prettify(), 'html.parser')
    rate_info.append(target_soup)
    
print(rate_info)