# src/bobbi_the_watchdog/packet_capture.py
from scapy.all import sniff  
from collections import defaultdict  
import logging  

def capture_packets(interface, duration):
    """
    Capture ICMP packets on the given interface for a set duration.
    Returns a dictionary of IP addresses and their packet counts.
    """
    try:
        # Capture packets, filtering for ICMP (e.g., pings)
        packets = sniff(iface=interface, timeout=duration, filter="icmp")
    except Exception as e:
        # Log an error if something goes wrong (e.g., wrong interface)
        logging.error(f"Failed to capture packets: {e}")
        return {}

    # Use a defaultdict to count packets from each IP
    ip_counts = defaultdict(int)
    for packet in packets:
        # Check if the packet has an IP layer
        if packet.haslayer("IP"):
            src_ip = packet["IP"].src  # Get source IP
            ip_counts[src_ip] += 1     # Increment count for this IP
            logging.info(f"ICMP packet from {src_ip}")  # Log the packet

    # Convert defaultdict to a regular dictionary and return
    return dict(ip_counts)