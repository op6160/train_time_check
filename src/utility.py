def list_to_multiline(train_messages):
    return "\n".join(train_messages)


from src.libs import get_html_content, logger
from bs4 import BeautifulSoup
def get_soup_by_url(url, load_time = 1):
    html = get_html_content(url = url, load_time = load_time)
    soup = BeautifulSoup(html, 'html.parser')
    return soup