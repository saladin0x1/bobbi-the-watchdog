# -*- coding: utf-8 -*-
# src/bobbi_the_watchdog/main.py

"""
Bobbi The Watchdog - Systeme de detection de menaces reseau

Ce module principal coordonne la detection d'attaques DDoS via l'analyse ICMP
et la detection de logiciels malveillants via l'analyse TCP.

Architecture:
    - Utilisation de threads pour la surveillance parallele (ICMP et TCP)
    - Logging centralise pour le suivi des activites
    - Gestion robuste des erreurs et des interruptions
"""

import logging
import bobbi_the_watchdog
import time
import threading
import os
import shutil
from .config.config import INTERFACE, THREAT_THRESHOLD
from .core.packet_capture import capture_icmp_packets, capture_tcp_and_analyze_live
from .core.threat_detection import ThreatDetection
from .core.malware_detection import MalwareDetection

def configure_logging(log_file_path: str) -> None:
    """
    Configure le systeme de journalisation avec un fichier et la sortie console.
    
    Args:
        log_file_path: Chemin du fichier de journalisation
    """
    # Suppression du repertoire si existant (cas d'erreur precedente)
    if os.path.isdir(log_file_path):
        shutil.rmtree(log_file_path)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler()
        ]
    )

def icmp_detection_worker(threat_detector: ThreatDetection, interface: str) -> None:
    """
    Travailleur pour la detection des menaces ICMP.
    Analyse en continu les paquets ICMP pour detecter les attaques DDoS.
    
    Args:
        threat_detector: Instance du detecteur de menaces
        interface: Interface reseau a surveiller
    """
    try:
        while True:
            logging.info(f"Demarrage de la detection ICMP sur {interface} pour 60 secondes...")
            # Capture et analyse des paquets ICMP
            ip_counts = capture_icmp_packets(interface, duration=60)
            threats = threat_detector.detect_threats(ip_counts)
            
            if threats:
                logging.warning(f"Attaques DDoS potentielles detectees depuis: {', '.join(threats)}")
            else:
                logging.info("Aucune menace DDoS detectee dans cet intervalle.")
            
            # Pause courte entre les cycles
            time.sleep(5)
            
    except KeyboardInterrupt:
        logging.info("Arret du travailleur de detection ICMP...")
    except Exception as e:
        logging.error(f"Erreur du travailleur ICMP: {e}")

def tcp_analysis_worker(malware_detector: MalwareDetection, interface: str) -> None:
    """
    Travailleur pour l'analyse des flux TCP.
    Surveille en continu le trafic TCP pour detecter les logiciels malveillants.
    
    Args:
        malware_detector: Instance du detecteur de malware
        interface: Interface reseau a surveiller
    """
    try:
        logging.info(f"Demarrage de la detection de malware TCP sur {interface}.")
        capture_tcp_and_analyze_live(interface, malware_detector, duration=None)
    except KeyboardInterrupt:
        logging.info("Arret du travailleur d'analyse TCP...")
    except Exception as e:
        logging.error(f"Erreur du travailleur TCP: {e}")

def main():
    """
    Point d'entree principal de Bobbi The Watchdog.
    Initialise et coordonne les composants de detection de menaces.
    """
    # Configuration du logging
    log_file_path = "network_log.txt"
    configure_logging(log_file_path)
    
    logging.info(f"Demarrage de Bobbi The Watchdog sur l'interface {INTERFACE}")
    print(bobbi_the_watchdog.__doc__)

    # Initialisation des detecteurs
    threat_detector = ThreatDetection(THREAT_THRESHOLD)
    malware_detector = MalwareDetection(log_file="network_log.txt")

    try:
        # Demarrage des travailleurs dans des threads separes
        icmp_thread = threading.Thread(
            target=icmp_detection_worker,
            args=(threat_detector, INTERFACE),
            daemon=True
        )
        tcp_thread = threading.Thread(
            target=tcp_analysis_worker,
            args=(malware_detector, INTERFACE),
            daemon=True
        )
        
        logging.info("Demarrage des threads d'analyse ICMP et TCP...")
        icmp_thread.start()
        tcp_thread.start()
        
        # Maintien du thread principal actif et surveillance des workers
        while True:
            time.sleep(1)
            if not icmp_thread.is_alive() and not tcp_thread.is_alive():
                logging.warning("Les deux threads de travail se sont arretes. Arret du programme...")
                break

    except KeyboardInterrupt:
        logging.info("Arret de Bobbi The Watchdog...")
    finally:
        logging.info("Bobbi The Watchdog a termine son execution.")

if __name__ == "__main__":
    main()