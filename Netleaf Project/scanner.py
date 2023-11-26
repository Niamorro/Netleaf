import concurrent.futures
import subprocess
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime

class ScannerThread(QThread):
    result_signal = pyqtSignal(str, str, int)

    def __init__(self, ip_start, ip_end):
        super().__init__()
        self.ip_start = ip_start
        self.ip_end = ip_end

    def run(self):
        total_ips = len(list(self.generate_ips(self.ip_start, self.ip_end)))
        progress_step = 100 / total_ips

        with concurrent.futures.ThreadPoolExecutor() as executor:
            devices = list(executor.map(self.ping_device, self.generate_ips(self.ip_start, self.ip_end)))
            progress_value = 0

            for device in devices:
                ip, status = device.split(" - ")
                self.result_signal.emit(ip, status, int(progress_value))
                progress_value += progress_step
                self.result_signal.emit("progress", "", int(progress_value))

    def generate_ips(self, ip_start, ip_end):
        start = int(ip_start.split('.')[-1])
        end = int(ip_end.split('.')[-1])

        for i in range(start, end + 1):
            yield f'{ip_start.rsplit(".", 1)[0]}.{i}'

    def ping_device(self, ip):
        try:
            start_time = datetime.now()
            subprocess.check_output(["ping", "-n", "1", ip], timeout=2)
            end_time = datetime.now()
            elapsed_time = end_time - start_time
            result = f'{ip} - active (Response Time: {elapsed_time})'
        except subprocess.CalledProcessError:
            result = f'{ip} - inactive'
        except subprocess.TimeoutExpired:
            result = f'{ip} - timeout'

        return result
