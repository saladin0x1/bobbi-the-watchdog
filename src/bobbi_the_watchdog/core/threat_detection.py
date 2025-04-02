# src/bobbi_the_watchdog/threat_detection.py
def detect_threats(ip_counts, threshold):
    """
    Check if any IP sent more ICMP packets than the threshold.
    Returns a list of suspicious IPs.
    """
    threats = [] 
    for ip, count in ip_counts.items():  
        if count > threshold:  
            threats.append(ip) 
    return threats