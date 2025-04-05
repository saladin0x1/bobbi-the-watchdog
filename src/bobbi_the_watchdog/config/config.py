# Configuration variables
# the interface is bridge100 for later shi 
INTERFACE = "eth1"         # Network interface to monitor (change to yours, e.g.) "eth1 in the alpine container")
CAPTURE_DURATION = 20      # How long to capture packets (in seconds !!!!!!!!!!!!!!!)
THREAT_THRESHOLD = 50    # Max ICMP packets from one IP before flagging as a threat ,check the wiresharks docs or idc ask gpt
