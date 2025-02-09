# port_scanner.py
from scapy.all import IP, TCP, sr1
from PySide6.QtCore import QObject, Signal
from concurrent.futures import ThreadPoolExecutor
import socket
from threading import Lock

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
        self.lock = Lock()

    def scan_port(self, port):
        try:
            tcp_request = IP(dst=self.ip) / TCP(dport=port, flags="S")
            with self.lock:
                response = sr1(tcp_request, timeout=self.timeout, verbose=False)
            
            if response and response.haslayer(TCP):
                if response[TCP].flags & 0x12:  # SYN-ACK
                    service = self.get_service_name(port)
                    return port, "Open", service
                elif response[TCP].flags & 0x14:  # RST-ACK
                    return port, "Closed", ""
            return port, "Filtered", ""
        except Exception as e:
            return port, f"Error: {str(e)}", ""

    def get_service_name(self, port):
        try:
            return socket.getservbyport(port)
        except:
            return "Unknown"

    def run_scan(self):
        total_ports = self.end_port - self.start_port + 1
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.scan_port, port) 
                      for port in range(self.start_port, self.end_port + 1)]
            
            for i, future in enumerate(futures):
                try:
                    port, status, service = future.result()
                    self.result_signal.emit(self.ip, port, status, service)
                    progress = int((i + 1) / total_ports * 100)
                    self.progress_signal.emit(progress)
                except Exception as e:
                    print(f"Error processing future: {str(e)}")

class PortScannerThread(QObject):
    finished = Signal()

    def __init__(self, ip, start_port, end_port, settings):
        super().__init__()
        self.scanner = PortScanner(ip, start_port, end_port, settings)
        self.result_signal = self.scanner.result_signal
        self.progress_signal = self.scanner.progress_signal

    def run(self):
        try:
            self.scanner.run_scan()
        except Exception as e:
            print(f"Error in scanner thread: {str(e)}")
        finally:
            self.finished.emit()