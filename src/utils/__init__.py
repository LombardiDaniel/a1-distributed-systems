# ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk '{print $2}' 
from .constants import DATETIME_LOG_FORMAT, LOG_FORMAT
from .recieves import show_text, show_video
from .utils import Utils
