import re

def re_form(startswith = "", endswith = ""):
    return re.compile(r'^'+startswith+r'.*'+endswith)

# text processing utility
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

# data processing utility 
def soup_find_all_div_by_id(soup, id):
    return soup.find_all("div", id = id)