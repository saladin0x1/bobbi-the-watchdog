# src/bobbi_the_watchdog/main.py
import logging
import bobbi_the_watchdog
from .config.config import INTERFACE, CAPTURE_DURATION, THREAT_THRESHOLD
from .core.packet_capture import capture_icmp_packets, capture_tcp_file
from .core.threat_detection import ThreatDetection
from .core.malware_detection import MalwareDetection

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("network_log.txt"),
            logging.StreamHandler()
        ]
    )

    # Start the program
    print(bobbi_the_watchdog.__doc__)  # Print the docstring from __init__.py
    logging.info("Starting Bobbi the Watchdog")

    # Part 1: Capture ICMP packets and detect DDoS threats
    logging.info(f"Capturing ICMP packets on {INTERFACE} for {CAPTURE_DURATION} seconds")
    ip_counts = capture_icmp_packets(INTERFACE, CAPTURE_DURATION)
    threat_detector = ThreatDetection(THREAT_THRESHOLD)
    threats = threat_detector.detect_threats(ip_counts)
    if threats:
        logging.warning(f"Potential DDoS attacks detected from: {', '.join(threats)}")
    else:
        logging.info("No DDoS threats detected.")

    # Part 2: Capture TCP packets and detect malware
    logging.info(f"Capturing TCP packets on {INTERFACE} for {CAPTURE_DURATION} seconds")
    captured_file = capture_tcp_file(INTERFACE, CAPTURE_DURATION)
    if captured_file:
        malware_detector = MalwareDetection(log_file="network_log.txt")
        result = malware_detector.analyze_file(captured_file)
        if result["is_malware"]:
            logging.warning(f"Potential malware detected: {result}")
        else:
            logging.info(f"No malware detected: {result}")
    else:
        logging.info("No file captured for malware analysis.")

    logging.info("Finished")

if __name__ == "__main__":
    main()