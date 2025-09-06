"""
Cybersecurity Intrusion Detection System

Features:
- Network packet analysis
- Anomaly detection
- Alerting
- Modular design
- CLI interface
- Error handling
"""
import socket
import sys
import threading
import time
import random
from collections import deque

class PacketSniffer:
    def __init__(self, iface='lo'):
        self.iface = iface
        self.running = False
        self.packets = deque(maxlen=1000)

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.sniff, daemon=True)
        self.thread.start()

    def sniff(self):
        try:
            s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
            s.bind((self.iface, 0))
            while self.running:
                pkt, _ = s.recvfrom(65565)
                self.packets.append(pkt)
        except Exception as e:
            print(f"Sniffing error: {e}")

    def stop(self):
        self.running = False

class AnomalyDetector:
    def __init__(self):
        self.baseline = random.randint(100, 200)

    def detect(self, packets):
        pkt_count = len(packets)
        if pkt_count > self.baseline * 2:
            return True, pkt_count
        return False, pkt_count

class AlertSystem:
    def alert(self, msg):
        print(f"ALERT: {msg}")

class CLI:
    @staticmethod
    def run():
        sniffer = PacketSniffer()
        detector = AnomalyDetector()
        alert = AlertSystem()
        print("Starting Intrusion Detection...")
        sniffer.start()
        try:
            while True:
                time.sleep(5)
                detected, count = detector.detect(sniffer.packets)
                print(f"Packet count: {count}")
                if detected:
                    alert.alert(f"Anomaly detected! Packet count: {count}")
        except KeyboardInterrupt:
            print("Stopping...")
            sniffer.stop()

if __name__ == "__main__":
    try:
        CLI.run()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
