import concurrent.futures
import subprocess
from PySide6.QtCore import QThread, Signal
from datetime import datetime
import socket
import ipaddress
import re
import platform


class ScannerThread(QThread):
    result_signal = Signal(str, str, str, float, int)

    def __init__(self, ip_start, ip_end, settings):
        super().__init__()
        self.ip_start = ip_start
        self.ip_end = ip_end
        self.settings = settings

    def generate_ips(self, ip_start, ip_end):
        start = ipaddress.IPv4Address(ip_start)
        end = ipaddress.IPv4Address(ip_end)

        for ip in range(int(start), int(end) + 1):
            yield str(ipaddress.IPv4Address(ip))

    def run(self):
        total_ips = len(list(self.generate_ips(self.ip_start, self.ip_end)))
        progress_step = 100 / total_ips

        max_workers = self.settings['Scanning'].get('Threads', 100)
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.scan_device, ip) for ip in self.generate_ips(self.ip_start, self.ip_end)]

            progress_value = 0

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                ip, status, mac, response_time = result
                self.result_signal.emit(ip, status, mac, response_time, int(progress_value))
                progress_value += progress_step
                self.result_signal.emit("progress", "", "", 0, int(progress_value))

    def scan_device(self, ip):
        try:
            for _ in range(self.settings['Scanning']['Attempts']):
                if self.settings['Scanning']['Protocols']['ARP']:
                    result = self.arp_scan(ip)
                    if result[1] == 'active':
                        return result

                if self.settings['Scanning']['Protocols']['ICMP']:
                    result = self.ping_device(ip)
                    if result[1] == 'active':
                        return result

                if self.settings['Scanning']['Protocols']['TCP']:
                    result = self.tcp_scan(ip)
                    if result[1] == 'active':
                        return result

                if self.settings['Scanning']['Protocols']['UDP']:
                    result = self.udp_scan(ip)
                    if result[1] == 'active':
                        return result

            return ip, 'inactive', '', 0
        except Exception as e:
            print(f"Error scanning {ip}: {e}")
            return ip, 'error', '', 0

    def ping_device(self, ip):
        try:
            start_time = datetime.now()
            if platform.system().lower() == 'windows':
                subprocess.check_output(["ping", "-n", "1", "-w", str(self.settings['Scanning']['ICMPTimeout']), ip], 
                                        timeout=self.settings['Scanning']['GeneralTimeout'], creationflags=0x08000000)
            else:
                subprocess.check_output(["ping", "-c", "1", "-W", str(self.settings['Scanning']['ICMPTimeout'] // 1000), ip], 
                                        timeout=self.settings['Scanning']['GeneralTimeout'])
            end_time = datetime.now()
            elapsed_time = (end_time - start_time).total_seconds()
            mac = self.get_mac(ip)
            return ip, 'active', mac, elapsed_time
        except subprocess.CalledProcessError:
            return ip, 'inactive', '', 0
        except subprocess.TimeoutExpired:
            return ip, 'timeout', '', 0
        except Exception as e:
            print(f"Error pinging {ip}: {e}")
            return ip, 'error', '', 0

    def tcp_scan(self, ip):
        for port in self.settings['Scanning']['TCPPorts']:
            try:
                start_time = datetime.now()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.settings['Scanning']['GeneralTimeout'])
                result = sock.connect_ex((ip, port))
                sock.close()
                end_time = datetime.now()
                elapsed_time = (end_time - start_time).total_seconds()
                if result == 0:
                    mac = self.get_mac(ip)
                    return ip, 'active', mac, elapsed_time
            except socket.timeout:
                continue
            except socket.error as e:
                print(f"Error scanning {ip}:{port}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error scanning {ip}:{port}: {e}")
                continue
        return ip, 'inactive', '', 0

    def udp_scan(self, ip):
        try:
            start_time = datetime.now()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.settings['Scanning']['GeneralTimeout'])
            sock.sendto(b'', (ip, 1))
            sock.recvfrom(1024)
            end_time = datetime.now()
            elapsed_time = (end_time - start_time).total_seconds()
            mac = self.get_mac(ip)
            return ip, 'active', mac, elapsed_time
        except socket.timeout:
            return ip, 'timeout', '', 0
        except socket.error:
            return ip, 'inactive', '', 0

    def arp_scan(self, ip):
        mac = self.get_mac(ip)
        if mac:
            return ip, 'active', mac, 0
        return ip, 'inactive', '', 0

    def get_mac(self, ip):
        try:
            if platform.system().lower() == 'windows':
                # Для Windows используем команду arp
                result = subprocess.check_output(f"arp -a {ip}", shell=True)
                try:
                    result = result.decode('utf-8')
                except UnicodeDecodeError:
                    result = result.decode('utf-8', errors='ignore')
                match = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", result)
                if match:
                    return match.group()
            else:
                # Для Linux и macOS используем команду arp
                result = subprocess.check_output(["arp", "-n", ip])
                try:
                    result = result.decode('utf-8')
                except UnicodeDecodeError:
                    result = result.decode('utf-8', errors='ignore')
                match = re.search(r"(([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}))", result)
                if match:
                    return match.group()
            return ''
        except subprocess.CalledProcessError:
            # Если команда arp завершилась с ошибкой, вероятно, MAC-адрес не найден
            return ''
        except Exception as e:
            print(f"Error getting MAC for {ip}: {e}")
            return ''