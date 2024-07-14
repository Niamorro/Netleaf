import socket
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import QObject, Signal

class PortScanner(QObject):
    result_signal = Signal(str, int, str, str)
    progress_signal = Signal(int)

    def __init__(self, ip, start_port, end_port, settings):
        super().__init__()
        self.ip = ip
        self.start_port = start_port
        self.end_port = end_port
        self.settings = settings
        self.timeout = settings['Scanning'].get('GeneralTimeout', 1)
        self.threads = settings['Scanning'].get('Threads', 100)

    def scan_port(self, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                result = s.connect_ex((self.ip, port))
                if result == 0:
                    service = self.get_service_name(port)
                    return port, "Open", service
                else:
                    return port, "Closed", ""
        except Exception as e:
            return port, f"Error: {str(e)}", ""

    def get_service_name(self, port):
        try:
            return socket.getservbyport(port)
        except (socket.error, OSError):
            # socket.error для Python 2, OSError для Python 3
            return "Unknown"
        except OverflowError:
            # Если порт находится вне допустимого диапазона
            return "Invalid Port"

    def run_scan(self):
        total_ports = self.end_port - self.start_port + 1
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.scan_port, port) for port in range(self.start_port, self.end_port + 1)]
            
            for i, future in enumerate(futures):
                port, status, service = future.result()
                self.result_signal.emit(self.ip, port, status, service)
                progress = int((i + 1) / total_ports * 100)
                self.progress_signal.emit(progress)

class PortScannerThread(QObject):
    finished = Signal()

    def __init__(self, ip, start_port, end_port, settings):
        super().__init__()
        self.scanner = PortScanner(ip, start_port, end_port, settings)

    def run(self):
        self.scanner.run_scan()
        self.finished.emit()