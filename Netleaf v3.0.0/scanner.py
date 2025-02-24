# scanner.py
from scapy.all import ARP, ICMP, TCP, UDP, IP, sr1, srp1, sr
from scapy.layers.inet import Ether
from PySide6.QtCore import QThread, Signal
from datetime import datetime
from mac_vendor_lookup import MacLookup, BaseMacLookup
import socket
import ipaddress
import concurrent.futures

class ScannerThread(QThread):
    result_signal = Signal(str, str, str, float, int, str, str)

    def __init__(self, ip_start, ip_end, settings):
        super().__init__()
        self.ip_start = ip_start
        self.ip_end = ip_end
        self.settings = settings
        BaseMacLookup.cache_path = "mac-vendors.txt"
        self.mac_lookup = MacLookup()
        try:
            self.mac_lookup.load_vendors()
        except:
            self.mac_lookup.update_vendors()

    def generate_ips(self, ip_start, ip_end):
        start = ipaddress.IPv4Address(ip_start)
        end = ipaddress.IPv4Address(ip_end)
        return [str(ipaddress.IPv4Address(ip)) for ip in range(int(start), int(end) + 1)]

    def run(self):
        ips = self.generate_ips(self.ip_start, self.ip_end)
        total_ips = len(ips)
        progress_step = 100 / total_ips

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.settings['Scanning'].get('Threads', 100)) as executor:
            # Scanning list
            futures = []
            for ip in ips:
                protocol_futures = []
                if self.settings['Scanning']['Protocols']['ARP']:
                    protocol_futures.append(executor.submit(self.arp_scan, ip))
                if self.settings['Scanning']['Protocols']['ICMP']:
                    protocol_futures.append(executor.submit(self.ping_device, ip))
                if self.settings['Scanning']['Protocols']['TCP']:
                    protocol_futures.append(executor.submit(self.tcp_scan, ip))
                if self.settings['Scanning']['Protocols']['UDP']:
                    protocol_futures.append(executor.submit(self.udp_scan, ip))
                futures.append((ip, protocol_futures))

            # Results
            for i, (ip, protocol_futures) in enumerate(futures):
                device_found = False
                for future in concurrent.futures.as_completed(protocol_futures):
                    result = future.result()
                    if result[1] == 'active':
                        device_found = True
                        device_name = self.get_device_name(ip)
                        manufacturer = self.get_manufacturer(result[2])
                        self.result_signal.emit(ip, result[1], result[2], result[3], 
                                             int(i * progress_step), device_name, manufacturer)
                        break

                if not device_found:
                    self.result_signal.emit(ip, 'inactive', '', 0, 
                                         int(i * progress_step), '', '')

                self.result_signal.emit("progress", "", "", 0, 
                                     int((i + 1) * progress_step), "", "")

    def arp_scan(self, ip):
        try:
            start_time = datetime.now()
            arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
            response = srp1(arp_request, timeout=self.settings['Scanning']['GeneralTimeout'], verbose=False)
            end_time = datetime.now()
            
            if response:
                return ip, 'active', response[ARP].hwsrc, (end_time - start_time).total_seconds()
            return ip, 'inactive', '', 0
        except Exception as e:
            print(f"ARP scan error for {ip}: {e}")
            return ip, 'error', '', 0

    def ping_device(self, ip):
        try:
            start_time = datetime.now()
            icmp_request = IP(dst=ip) / ICMP()
            response = sr1(icmp_request, timeout=self.settings['Scanning']['ICMPTimeout'] / 1000, verbose=False)
            end_time = datetime.now()
            
            if response:
                mac = self.get_mac_from_ip(ip)
                return ip, 'active', mac, (end_time - start_time).total_seconds()
            return ip, 'timeout', '', 0
        except Exception as e:
            print(f"ICMP scan error for {ip}: {e}")
            return ip, 'error', '', 0

    def tcp_scan(self, ip):
        for port in self.settings['Scanning']['TCPPorts']:
            try:
                start_time = datetime.now()
                tcp_request = IP(dst=ip) / TCP(dport=port, flags="S")
                response = sr1(tcp_request, timeout=self.settings['Scanning']['GeneralTimeout'], verbose=False)
                end_time = datetime.now()
                
                if response and response.haslayer(TCP) and response[TCP].flags & 0x12:
                    mac = self.get_mac_from_ip(ip)
                    return ip, 'active', mac, (end_time - start_time).total_seconds()
            except Exception as e:
                print(f"TCP scan error for {ip}:{port}: {e}")
                continue
        return ip, 'inactive', '', 0

    def udp_scan(self, ip):
        try:
            start_time = datetime.now()
            udp_request = IP(dst=ip) / UDP(dport=53)
            response = sr1(udp_request, timeout=self.settings['Scanning']['GeneralTimeout'], verbose=False)
            end_time = datetime.now()
            
            if response:
                mac = self.get_mac_from_ip(ip)
                return ip, 'active', mac, (end_time - start_time).total_seconds()
            return ip, 'timeout', '', 0
        except Exception as e:
            print(f"UDP scan error for {ip}: {e}")
            return ip, 'error', '', 0

    def get_mac_from_ip(self, ip):
        arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip)
        response = srp1(arp_request, timeout=1, verbose=False)
        if response and response.haslayer(ARP):
            return response[ARP].hwsrc
        return ''

    def get_device_name(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return ""

    def get_manufacturer(self, mac):
        if not mac:
            return ""
        try:
            return self.mac_lookup.lookup(mac)
        except:
            return ""