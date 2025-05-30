# -*- coding: utf-8 -*-
# src/bobbi_the_watchdog/config/config.py

"""
Configuration centralisee pour Bobbi The Watchdog.

Ce module definit les variables de configuration globales utilisees
par le systeme de detection de menaces. Les valeurs peuvent etre
modifiees via des variables d'environnement.

Variables:
    INTERFACE: Interface reseau a surveiller
    THREAT_THRESHOLD: Seuil de paquets ICMP avant detection d'une menace
"""

import os
from typing import Final

# Interface reseau par defaut dans le conteneur Ubuntu (eth0)
# Peut etre modifiee par la variable d'environnement INTERFACE
INTERFACE: Final[str] = os.getenv("INTERFACE", "eth0")

# Seuil de detection de menace - nombre maximum de paquets ICMP
# autorises depuis une meme IP avant d'etre considere comme menace
# Peut etre modifie par la variable d'environnement THREAT_THRESHOLD
THREAT_THRESHOLD: Final[int] = int(os.getenv("THREAT_THRESHOLD", "50"))
