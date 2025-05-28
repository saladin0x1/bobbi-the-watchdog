# Configuration variables
import os

# Default interface in Ubuntu container is eth0, but can be overridden by environment variable
INTERFACE = os.getenv("INTERFACE", "eth0")  # Network interface to monitor
# CAPTURE_DURATION = 20      # How long to capture packets (in seconds)
THREAT_THRESHOLD = int(os.getenv("THREAT_THRESHOLD", "50"))  # Max ICMP packets from one IP before flagging as a threat
