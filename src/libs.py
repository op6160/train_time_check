import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.dirname(current_dir)

submodule_path = os.path.join(project_root, 'libs', 'utility_python')

if submodule_path not in sys.path:
    sys.path.insert(0, submodule_path)

from src.logger_lib import log_msg as log
from src.time_lib import detail
from src.browser_lib import headers, connection_test, get_html_content

# import src.module.printer as printer
# from src.module.printer import log_msg as log
# from src.module.time_lib import detail
# from src.module.connection import headers, connection_test
# from src.module.browser import get_html_content