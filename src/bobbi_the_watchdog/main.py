import logging  
import bobbi_the_watchdog
from .config.config import INTERFACE, CAPTURE_DURATION, THREAT_THRESHOLD
from .core.packet_capture import capture_packets  
from .core.threat_detection import detect_threats  
def main():
    # stop copy pasting and read docs https://docs.python.org/3/howto/logging.html
    logging.basicConfig(
        level=logging.INFO, 
        format="%(asctime)s - %(levelname)s - %(message)s",  
        handlers=[
            logging.FileHandler("network_log.txt"),  
            logging.StreamHandler()  
        ]
    )
    # Start the program
    print(bobbi_the_watchdog.__doc__)  # Print the docstring from __init__.py 'missin around'
    logging.info("Starting Bobbi the Watchdog")
    logging.info(f"Capturing packets on {INTERFACE} for {CAPTURE_DURATION} seconds")
    # Capture packets and get IP counts
    ip_counts = capture_packets(INTERFACE, CAPTURE_DURATION)
    # Check for threats
    threats = detect_threats(ip_counts, THREAT_THRESHOLD)
    # Report results
    if threats:  # If the threats list isn’t empty
        logging.warning(f"Potential DDoS attacks detected from: {', '.join(threats)}")
    else:
        logging.info("No threats detected.")

    logging.info("Finished")
if __name__ == "__main__":
    main()  # Run the main function when the script is executed