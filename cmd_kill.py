import psutil
from psutil import process_iter
from signal import SIGTERM # or SIGKILL
import signal
# from signal import SIGKILL

# had to use try, except since it is giving a Accessdenied Error

def kill():   
    for proc in process_iter():
        try:
            for conns in proc.connections(kind='inet'):
                if conns.laddr.port == 8080:
                    proc.send_signal(SIGTERM) # or SIGKILL
                    continue
        except(PermissionError, psutil.AccessDenied):
            pass