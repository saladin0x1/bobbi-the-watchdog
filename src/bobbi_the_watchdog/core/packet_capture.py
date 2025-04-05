# src/bobbi_the_watchdog/core/packet_capture.py
from scapy.all import sniff
import logging
import socket
import os
from collections import defaultdict

def get_container_ip():
    """
    Retrieve the container's own IP address dynamically.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        logging.info(f"Detected container IP: {ip}")
        return ip
    except Exception as e:
        logging.error(f"Failed to detect container IP: {e}")
        return None

def capture_icmp_packets(interface, duration):
    """
    Capture ICMP packets on the given interface for a set duration.
    Returns a dictionary of IP addresses and their packet counts.
    """
    container_ip = get_container_ip()
    if not container_ip:
        logging.warning("Could not determine container IP; proceeding without filtering.")

    try:
        packets = sniff(iface=interface, timeout=duration, filter="icmp")
    except Exception as e:
        logging.error(f"Failed to capture ICMP packets: {e}")
        return {}

    ip_counts = defaultdict(int)
    for packet in packets:
        if packet.haslayer("IP"):
            src_ip = packet["IP"].src
            if container_ip and src_ip == container_ip:
                logging.debug(f"Ignoring packet from self: {src_ip}")
                continue
            ip_counts[src_ip] += 1
            logging.info(f"ICMP packet from {src_ip}")

    return dict(ip_counts)

def capture_tcp_file(interface, duration, output_dir="captured_files"):
    """
    Capture TCP packets on the given interface for a set duration and reassemble them into a file.
    Returns the path to the captured file or None if no file is captured.
    """
    container_ip = get_container_ip()
    if not container_ip:
        logging.warning("Could not determine container IP; proceeding without filtering.")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_data = b""

    def packet_handler(packet):
        nonlocal file_data
        if packet.haslayer("TCP") and packet.haslayer("Raw"):
            src_ip = packet["IP"].src if packet.haslayer("IP") else "unknown"
            if container_ip and src_ip == container_ip:
                logging.debug(f"Ignoring packet from self: {src_ip}")
                return
            payload = packet["Raw"].load
            file_data += payload
            logging.info(f"Captured {len(payload)} bytes from {src_ip}, total: {len(file_data)}")

    try:
        logging.info(f"Capturing TCP packets on {interface} for {duration} seconds")
        sniff(
            iface=interface,
            timeout=duration,
            filter="tcp port 80",
            prn=packet_handler
        )
    except Exception as e:
        logging.error(f"Failed to capture TCP packets: {e}")
        return None

    if file_data:
        output_file = os.path.join(output_dir, "captured_file")
        try:
            with open(output_file, "wb") as f:
                f.write(file_data)
            logging.info(f"File saved to {output_file}")
            return output_file
        except Exception as e:
            logging.error(f"Failed to save captured file: {e}")
            return None
    else:
        logging.info("No TCP data captured to save as a file")
        return None