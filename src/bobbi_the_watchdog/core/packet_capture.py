# src/bobbi_the_watchdog/core/packet_capture.py
from scapy.all import sniff, get_if_list # Changed import
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

def capture_icmp_packets(interface, duration=None):
    """
    Capture ICMP packets on the given interface.
    If duration is None, capture indefinitely until KeyboardInterrupt.
    Returns a dictionary of IP addresses and their packet counts.
    """
        
    container_ip = get_container_ip()
    if not container_ip:
        logging.warning("Could not determine container IP; proceeding without filtering.")

    try:
        if duration is None:
            logging.info(f"Capturing ICMP packets on {interface} indefinitely...")
            packets = sniff(iface=interface, filter="icmp", store=True) # Removed timeout for indefinite capture
        else:
            logging.info(f"Capturing ICMP packets on {interface} for {duration} seconds...")
            packets = sniff(iface=interface, timeout=duration, filter="icmp")
    except KeyboardInterrupt:
        logging.info("Packet capture interrupted by user.")
        # If interrupted, process packets captured so far
        # Scapy might store partial captures in a global or we might need to handle this differently
        # For now, assume sniff returns what it has upon interruption if store=True, or an empty list if not.
        # This part might need refinement based on how Scapy handles Ctrl+C with no timeout.
        return {}
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

# def capture_tcp_file(interface, duration=None, output_dir="captured_files"):
def capture_tcp_and_analyze_live(interface, malware_detector, duration=None):
    """
    Capture TCP packets on the given interface and analyze them live for malware.
    If duration is None, capture indefinitely until KeyboardInterrupt.
    """
    container_ip = get_container_ip()
    if not container_ip:
        logging.warning("Could not determine container IP for TCP capture; proceeding without filtering.")

    def live_packet_handler(packet):
        if packet.haslayer("TCP") and packet.haslayer("Raw") and packet.haslayer("IP"):
            src_ip = packet["IP"].src
            dst_ip = packet["IP"].dst
            sport = packet["TCP"].sport
            dport = packet["TCP"].dport
            payload = packet["Raw"].load

            if container_ip and (src_ip == container_ip or dst_ip == container_ip):
                # Skip packets to/from self
                return

            # For simplicity, we'll analyze each packet's payload individually here.
            # More advanced stream reassembly would be needed for stateful analysis.
            if payload:
                logging.info(f"Received TCP data chunk: {len(payload)} bytes from {src_ip}:{sport} to {dst_ip}:{dport}")
                malware_detector.analyze_data_chunk(payload)

    try:
        if duration is None:
            logging.info(f"Starting live TCP packet capture and analysis on {interface} indefinitely...")
            sniff(iface=interface, filter="tcp", prn=live_packet_handler, store=False)
        else:
            logging.info(f"Starting live TCP packet capture and analysis on {interface} for {duration} seconds...")
            sniff(iface=interface, filter="tcp", prn=live_packet_handler, store=False, timeout=duration)
    except KeyboardInterrupt:
        logging.info("Live TCP packet capture and analysis interrupted by user.")
    except Exception as e:
        logging.error(f"Error during live TCP packet capture and analysis: {e}")

# Old function, can be removed or kept if file-based capture is still needed elsewhere
# def capture_tcp_file(interface, duration=None, output_dir="captured_files"):
#     ...