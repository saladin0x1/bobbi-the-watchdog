# -*- coding: utf-8 -*-
# src/bobbi_the_watchdog/core/packet_capture.py

"""
Module de capture de paquets reseau pour Bobbi The Watchdog.

Ce module fournit les fonctionnalites de capture de paquets ICMP et TCP
en utilisant la bibliotheque Scapy. Il inclut:
    - La capture des paquets ICMP pour la detection DDoS
    - La capture des flux TCP pour l'analyse de malware
    - La detection dynamique de l'adresse IP du conteneur
"""

from scapy.all import sniff, get_if_list, Packet
import logging
import socket
import os
from collections import defaultdict
from typing import Dict, Optional, List, Callable, NoReturn
from .malware_detection import MalwareDetection

def get_container_ip() -> Optional[str]:
    """
    Recupere dynamiquement l'adresse IP du conteneur.
    
    Returns:
        Optional[str]: L'adresse IP du conteneur ou None en cas d'echec.
                      Utilisez 'if ip is not None' pour verifier la valeur.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connection a Google DNS pour obtenir l'IP locale
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        
        if not isinstance(ip, str):
            logging.error("L'IP recuperee n'est pas une chaine de caracteres")
            return None
            
        logging.info(f"IP du conteneur identifiee: {ip}")
        return ip
    except Exception as e:
        logging.error(f"Echec de detection de l'IP du conteneur: {e}")
        return None

def capture_icmp_packets(interface: str, duration: Optional[int] = None) -> Dict[str, int]:
    """
    Capture les paquets ICMP sur l'interface specifique.
    
    Args:
        interface: Interface reseau a surveiller
        duration: Duree de capture en secondes.
                 Si None, capture indefiniment jusqu'a interruption.
    
    Returns:
        Dict[str, int]: Dictionnaire des adresses IP et leur nombre de paquets.
                       Retourne un dictionnaire vide en cas d'erreur.
    """
    # Initialisation du compteur avec defaultdict
    ip_counts = defaultdict(int)
    container_ip: Optional[str] = get_container_ip()
    
    if container_ip is None:
        logging.warning("Impossible de determiner l'IP du conteneur; poursuite sans filtrage.")

    try:
        # Configuration de la capture selon la duree specifiee
        capture_params = {
            "iface": interface,
            "filter": "icmp",
            "store": True
        }
        
        if duration is not None:
            capture_params["timeout"] = duration
            logging.info(f"Capture des paquets ICMP sur {interface} pour {duration} secondes...")
        else:
            logging.info(f"Capture des paquets ICMP sur {interface} en mode indefini...")
        
        packets: List[Packet] = sniff(**capture_params)

        # Analyse des paquets captures
        for packet in packets:
            if packet.haslayer("IP"):
                src_ip = packet["IP"].src
                if container_ip is not None and src_ip == container_ip:
                    logging.debug(f"Ignorons le paquet de nous-memes: {src_ip}")
                    continue
                ip_counts[src_ip] += 1
                logging.debug(f"Paquet ICMP recu de {src_ip}")

        # Conversion en dictionnaire standard pour l'interface
        return dict(ip_counts)

    except KeyboardInterrupt:
        logging.info("Capture de paquets interrompue par l'utilisateur.")
        return dict(ip_counts)
    except Exception as e:
        logging.error(f"Echec de la capture de paquets ICMP: {e}")
        return {}

def capture_tcp_and_analyze_live(
    interface: str,
    malware_detector: MalwareDetection,
    duration: Optional[int] = None
) -> None:
    """
    Capture les paquets TCP sur l'interface et analyse les flux pour detecter les malwares.
    
    Args:
        interface: Interface reseau a surveiller
        malware_detector: Instance du detecteur de malware
        duration: Duree de capture en secondes.
                 Si None, capture indefiniment jusqu'a interruption.
    """
    container_ip: Optional[str] = get_container_ip()
    if container_ip is None:
        logging.warning("Impossible de determiner l'IP pour la capture TCP; poursuite sans filtrage.")

    def live_packet_handler(packet: Packet) -> None:
        """
        Gestionnaire de paquets en temps reel pour l'analyse TCP.
        Analyse chaque paquet pour detecter des signatures de malware.
        
        Args:
            packet: Paquet reseau capture par Scapy
        """
        if not all(packet.haslayer(layer) for layer in ["TCP", "Raw", "IP"]):
            return

        src_ip: str = packet["IP"].src
        dst_ip: str = packet["IP"].dst
        sport: int = packet["TCP"].sport
        dport: int = packet["TCP"].dport
        payload: bytes = packet["Raw"].load

        if container_ip is not None and (src_ip == container_ip or dst_ip == container_ip):
            # Ignore les paquets provenant ou destines au conteneur
            return

        # Creation d'un identifiant unique pour la connexion TCP
        flow_id: str = f"{src_ip}:{sport}-{dst_ip}:{dport}"
        
        try:
            # Analyse du contenu pour la detection de malware
            if malware_detector.analyze_stream(payload, flow_id):
                logging.warning(
                    f"Malware potentiel detecte dans le flux TCP: {flow_id}"
                )
        except Exception as e:
            logging.error(f"Erreur lors de l'analyse du flux TCP {flow_id}: {e}")

    try:
        logging.info(f"Demarrage de la capture TCP sur {interface}")
        # Capture en continu avec le gestionnaire de paquets
        capture_params = {
            "iface": interface,
            "filter": "tcp",
            "prn": live_packet_handler,
            "store": 0
        }
        
        if duration is not None:
            capture_params["timeout"] = duration
            
        sniff(**capture_params)
    except KeyboardInterrupt:
        logging.info("Analyse TCP interrompue par l'utilisateur")
    except Exception as e:
        logging.error(f"Erreur lors de la capture TCP: {e}")