# src/bobbi_the_watchdog/main.py
import logging
import bobbi_the_watchdog
import time # Added for the main loop
from .config.config import INTERFACE, THREAT_THRESHOLD
# from .core.packet_capture import capture_icmp_packets, capture_tcp_file # Old import
from .core.packet_capture import capture_icmp_packets, capture_tcp_and_analyze_live # New import
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

    try:
        # Continuous loop for ICMP and TCP analysis
        # Note: The sniff functions in packet_capture are blocking if duration is None.
        # To run them truly concurrently or in a more complex loop, threading/async would be needed.
        # For now, we'll demonstrate a conceptual continuous run. 
        # If capture_icmp_packets is set to run indefinitely, it will block the loop.
        # For a real live system, these would likely be separate threads/processes.

        # For simplicity, let's assume we want to run captures in a loop, 
        # but sniff(..., duration=None) will block. 
        # The previous change made duration=None the default for indefinite capture.
        # If we want both ICMP and TCP live, they need to run in parallel (e.g., threads).
        # The current structure will run ICMP capture, then TCP capture sequentially if both are indefinite.

        # To make it truly endless and live for both, we'd need to restructure significantly
        # using threading or asyncio. The current request implies a single-threaded loop.
        # The `capture_tcp_and_analyze_live` will now block if duration is None.
        # The `capture_icmp_packets` will also block if duration is None.

        # Option 1: Run TCP live analysis indefinitely (blocks further code in this thread)
        logging.info(f"Starting live TCP malware detection on {INTERFACE}.")
        capture_tcp_and_analyze_live(INTERFACE, malware_detector, duration=None) # Runs indefinitely

        # ICMP detection would not be reached if TCP analysis runs indefinitely above.
        # To have both, they must be in separate threads or use non-blocking calls
        # with a manual loop, which sniff doesn't directly support for continuous processing
        # without blocking.

        # For a simplified "endless" run where one follows the other (if the first one ever finishes):
        # while True: 
        #     logging.info(f"Starting ICMP threat detection on {INTERFACE}.")
        #     ip_counts = capture_icmp_packets(INTERFACE, duration=60) # Example: run for 60s then repeat
        #     threats = threat_detector.detect_threats(ip_counts)
        #     if threats:
        #         logging.warning(f"Potential DDoS attacks detected from: {', '.join(threats)}")
        #     else:
        #         logging.info("No DDoS threats detected in this interval.")
            
        #     # The TCP live analysis is now its own blocking call, so it can't be in a simple loop like this
        #     # with the ICMP part unless we give it a timeout.
        #     logging.info("Looping for next capture cycle or stopping TCP if it had a timeout.")
        #     time.sleep(10) # Pause before next cycle if not using indefinite blocking calls

    except KeyboardInterrupt:
        logging.info("Bobbi the Watchdog is shutting down...")
    finally:
        logging.info("Bobbi the Watchdog has finished.")

if __name__ == "__main__":
    main()