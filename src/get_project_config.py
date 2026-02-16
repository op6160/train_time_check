import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from config import (
    go_up_keyword,
    go_down_keyword,
    fine_keyword,
    BASE_URL,
    STATE_URL,
)

if __name__ == "__main__":
    print(go_up_keyword)
    print(go_down_keyword)
    print(fine_keyword)
    print(BASE_URL)
    print(STATE_URL)