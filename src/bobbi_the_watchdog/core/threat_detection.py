# -*- coding: utf-8 -*-
# src/bobbi_the_watchdog/core/threat_detection.py

"""
Module de detection des menaces pour Bobbi The Watchdog.

Ce module gere la detection des attaques DDoS potentielles en analysant
le nombre de paquets ICMP par adresse IP source. Il utilise un seuil
configurable pour identifier les comportements suspects.
"""

import logging
from typing import Dict, List

class ThreatDetection:
    """
    Classe pour la detection des menaces DDoS basee sur l'analyse de trafic ICMP.
    
    Cette classe utilise un seuil configurable pour identifier les adresses IP
    qui envoient un nombre anormal de paquets ICMP, indiquant potentiellement
    une attaque par inondation.
    
    Attributes:
        threshold (int): Nombre maximum de paquets autorises avant detection
    """
    
    def __init__(self, threshold: int) -> None:
        """
        Initialise le detecteur de menaces.
        
        Args:
            threshold: Seuil de paquets ICMP avant detection d'une menace
        """
        self.threshold = threshold
        logging.info(f"Detecteur de menaces initialise avec un seuil de {threshold} paquets")

    def detect_threats(self, ip_counts: Dict[str, int]) -> List[str]:
        """
        Detecte les menaces DDoS potentielles basees sur le comptage de paquets.
        
        Cette methode analyse le nombre de paquets par adresse IP source et
        identifie celles qui depassent le seuil configure comme menaces potentielles.
        
        Args:
            ip_counts: Dictionnaire des adresses IP et leur nombre de paquets
        
        Returns:
            List[str]: Liste des adresses IP identifiees comme menaces
        """
        threats = []
        for ip, count in ip_counts.items():
            if count > self.threshold:
                threats.append(ip)
                logging.warning(
                    f"Menace detectee: {ip} a envoye {count} paquets ICMP "
                    f"(seuil: {self.threshold})"
                )
        
        if not threats:
            logging.debug("Aucune menace detectee dans ce cycle d'analyse")
        
        return threats