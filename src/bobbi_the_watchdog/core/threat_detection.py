# src/bobbi_the_watchdog/threat_detection.py
def detect_threats(ip_counts, threshold):
    """
    Check if any IP sent more ICMP packets than the threshold.
    Returns a list of suspicious IPs.
    """
    threats = []  # Empty list to store threatening IPs
    for ip, count in ip_counts.items():  # Loop through IPs and their counts
        if count > threshold:  # Compare count to threshold
            threats.append(ip)  # Add IP to list if it exceeds threshold
    return threats