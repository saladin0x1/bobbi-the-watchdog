# Configuration variables
# Default interface in Alpine container is eth0
INTERFACE = "en0"         # Network interface to monitor (default for Alpine container)
CAPTURE_DURATION = 20      # How long to capture packets (in seconds)
THREAT_THRESHOLD = 50    # Max ICMP packets from one IP before flagging as a threat
