import sys
import os
from datetime import datetime

# set path
src_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.dirname(src_path)
# submodule_path = os.path.join(root_path, 'libs', 'utility_python')

# # add submodule path
# if submodule_path not in sys.path:
#     sys.path.insert(0, submodule_path)

# import utility modules
from libs.utility_python.src.logger_lib import log_msg as log
from libs.utility_python.src.time_lib import detail
from libs.utility_python.src.browser_lib import headers, connection_test, get_html_content
from libs.utility_python.src.drive_lib import save_content, load_content, DiscordStrategy

# log setup
import logging

# log directory 
log_dir = os.path.join(root_path, "logs")
os.makedirs(log_dir, exist_ok=True)

# log filename
today_str = datetime.now().strftime("%Y-%m-%d")
log_filename = f"train_check_{today_str}.log"

# logger set
logger = logging.getLogger("TrainCheck")

# logger set handler
_handler = logging.StreamHandler(sys.stdout)
_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
_handler.setFormatter(_formatter)
_file_handler = logging.FileHandler(os.path.join(log_dir, log_filename), encoding='utf-8')
_file_handler.setFormatter(_formatter)

# logger add handler
logger.addHandler(_handler)
logger.addHandler(_file_handler)

# logger set level
logger.setLevel(logging.INFO)

(root_path,
 src_path,
#  submodule_path,
 log,
 detail,
 headers,
 connection_test,
 get_html_content,
 save_content,
 load_content,
 DiscordStrategy,
 logger,
 log_dir,
 log_filename)

__all__ = [
    "root_path",
    "src_path",
    "submodule_path",
    "log",
    "detail",
    "headers",
    "connection_test",
    "get_html_content",
    "save_content",
    "load_content",
    "DiscordStrategy",
    "logger",
    "log_dir",
    "log_filename",
]