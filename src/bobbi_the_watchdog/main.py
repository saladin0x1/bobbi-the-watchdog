# src/bobbi_the_watchdog/main.py
import logging
import bobbi_the_watchdog
import time
import threading
from .config.config import INTERFACE, THREAT_THRESHOLD
from .core.packet_capture import capture_icmp_packets, capture_tcp_and_analyze_live
from .core.threat_detection import ThreatDetection
from .core.malware_detection import MalwareDetection

def main():
    # Configure logging
    import os
    
    # Ensure log file is treated as a file, not directory
    log_file_path = "network_log.txt"
    
    # Remove if it exists as directory
    if os.path.isdir(log_file_path):
        import shutil
        shutil.rmtree(log_file_path)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )

    logging.info(f"Starting Bobbi the Watchdog on interface {INTERFACE}")
    print(bobbi_the_watchdog.__doc__)

    threat_detector = ThreatDetection(THREAT_THRESHOLD)
    # Initialize MalwareDetection once
    # It will use /app/network_log.txt inside the container for its own logging
    malware_detector = MalwareDetection(log_file="network_log.txt")

    def icmp_detection_worker():
        """Worker function for ICMP threat detection"""
        try:
            while True:
                logging.info(f"Starting ICMP threat detection on {INTERFACE} for 60 seconds...")
                ip_counts = capture_icmp_packets(INTERFACE, duration=60)
                threats = threat_detector.detect_threats(ip_counts)
                if threats:
                    logging.warning(f"Potential DDoS attacks detected from: {', '.join(threats)}")
                else:
                    logging.info("No DDoS threats detected in this interval.")
                time.sleep(5)  # Short pause between cycles
        except KeyboardInterrupt:
            logging.info("ICMP detection worker shutting down...")
        except Exception as e:
            logging.error(f"ICMP detection worker error: {e}")

    def tcp_analysis_worker():
        """Worker function for TCP malware analysis"""
        try:
            logging.info(f"Starting live TCP malware detection on {INTERFACE}.")
            capture_tcp_and_analyze_live(INTERFACE, malware_detector, duration=None)
        except KeyboardInterrupt:
            logging.info("TCP analysis worker shutting down...")
        except Exception as e:
            logging.error(f"TCP analysis worker error: {e}")

    try:
        # Start both workers in separate threads
        icmp_thread = threading.Thread(target=icmp_detection_worker, daemon=True)
        tcp_thread = threading.Thread(target=tcp_analysis_worker, daemon=True)
        
        logging.info("Starting ICMP and TCP analysis threads...")
        icmp_thread.start()
        tcp_thread.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            if not icmp_thread.is_alive() and not tcp_thread.is_alive():
                logging.warning("Both worker threads have stopped. Exiting...")
                break

    except KeyboardInterrupt:
        logging.info("Bobbi the Watchdog is shutting down...")
    finally:
        logging.info("Bobbi the Watchdog has finished.")

if __name__ == "__main__":
    main()