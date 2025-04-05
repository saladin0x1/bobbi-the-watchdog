# src/bobbi_the_watchdog/core/threat_detection.py
import logging

class ThreatDetection:
    def __init__(self, threshold):
        self.threshold = threshold

    def detect_threats(self, ip_counts):
        """
        Detect potential DDoS threats based on packet counts exceeding the threshold.
        Returns a list of IP addresses identified as threats.
        """
        threats = []
        for ip, count in ip_counts.items():
            if count > self.threshold:
                threats.append(ip)
                logging.info(f"Threat detected: {ip} sent {count} ICMP packets")
        return threats