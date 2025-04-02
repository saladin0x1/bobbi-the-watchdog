from scapy.all import sniff  
from collections import defaultdict  
import logging  
import socket  

def get_container_ip():
    """
    Retrieve the container's own IP address dynamically.
    In a Docker bridge network, this is typically the IP assigned to the default interface (e.g., eth0).
    """
    try:
        # Create a socket and connect to an external address to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Use Google's DNS as a dummy external address
        ip = s.getsockname()[0]
        s.close()
        logging.info(f"Detected container IP: {ip}")
        return ip
    except Exception as e:
        logging.error(f"Failed to detect container IP: {e}")
        return None

def capture_packets(interface, duration):
    """
    Capture ICMP packets on the given interface for a set duration.
    Returns a dictionary of IP addresses and their packet counts.
    """
    # Get the container's own IP address
    container_ip = get_container_ip()
    if not container_ip:
        logging.warning("Could not determine container IP; proceeding without filtering.")

    try:
        # Capture packets, filtering for ICMP (e.g., pings)
        packets = sniff(iface=interface, timeout=duration, filter="icmp")
    except Exception as e:
        # Log an error if something goes wrong (e.g., wrong interface)
        logging.error(f"Failed to capture packets: {e}")
        return {}

    # Use a defaultdict to count packets from each IP
    # In Python, defaultdict is a subclass of the built-in dict class.
    # It provides a dictionary-like object that returns a default value for nonexistent keys,
    # which helps prevent errors when trying to access or modify keys that haven't been added yet.
    #
    # When creating a defaultdict, you provide a factory function (a callable) that will generate 
    # default values for new keys. For example, you can use `int` to automatically initialize 
    # new keys to 0, or `list` to initialize new keys with an empty list.
    ip_counts = defaultdict(int)
    for packet in packets:
        # Check if the packet has an IP layer
        if packet.haslayer("IP"):
            src_ip = packet["IP"].src  # Get source IP
            # Skip packets from the container's own IP
            if container_ip and src_ip == container_ip:
                logging.debug(f"Ignoring packet from self: {src_ip}")
                continue
            ip_counts[src_ip] += 1     # Increment count for this IP
            logging.info(f"ICMP packet from {src_ip}")  # Log the packet

    # Convert defaultdict to a regular dictionary and return
    return dict(ip_counts)