# Rapport: Structures de données Python dans Bobbi The Watchdog

## Chapitre I: Cadre général du projet

### Introduction et objectifs
Bobbi the Watchdog est un système de détection de menaces réseau qui analyse les paquets pour identifier les attaques DDoS potentielles et la présence de logiciels malveillants. Le projet se compose de deux fonctionnalités principales:
1. Capture et analyse de paquets ICMP pour détecter les attaques DDoS
2. Capture et analyse de paquets TCP pour détecter les logiciels malveillants

Ce système est déployé sur des conteneurs Docker Alpine personnalisés sur une plage d'adresses IP spécifique. Les tests sont effectués sur l'hôte à l'aide des scripts présents dans le dossier Test, notamment pour simuler des attaques par flood et tester la détection de malwares.

### Description du problème
Le projet adresse deux problèmes de sécurité réseau essentiels:
- Détection des attaques par déni de service (DDoS) via l'analyse de trafic ICMP
- Détection de logiciels malveillants via l'analyse des fichiers transmis par TCP

### Approche générale
L'application utilise une approche modulaire avec des composants spécialisés pour:
- La capture de paquets réseau (utilisant la bibliothèque Scapy)
- La détection de menaces basée sur des seuils
- L'analyse de malware (utilisant ClamAV et des hachages SHA256)

### Architecture de la solution
Le projet est structuré en modules spécifiques:
- `main.py`: Point d'entrée coordonnant les différents modules
- `config/config.py`: Configuration centralisée
- `core/packet_capture.py`: Capture des paquets réseau
- `core/threat_detection.py`: Détection des menaces DDoS
- `core/malware_detection.py`: Analyse de logiciels malveillants

L'environnement de test comprend:
- `Test/flood.sh`: Script pour simuler des attaques DDoS par inondation ICMP
- `Test/https-server.py`: Serveur HTTPS pour tester le transfert de fichiers malveillants
- `Test/TEST_FILES/eicar.com.txt`: Fichier de test standard pour la détection de malwares

## Chapitre II: Conception

### Principes de conception
- **Modularité**: Séparation claire des responsabilités entre les différents composants
- **Simplicité**: Utilisation de structures de données natives de Python
- **Journalisation**: Système de logging détaillé pour le suivi des activités
- **Configuration centralisée**: Paramètres centralisés pour faciliter la personnalisation
- **Programmation orientée objet**: Utilisation de classes pour encapsuler les comportements et états des détecteurs

### Utilisation de la programmation orientée objet (OOP)

La programmation orientée objet a été utilisée dans ce projet pour plusieurs raisons stratégiques:

#### 1. Encapsulation des comportements et des données

Les classes `ThreatDetection` et `MalwareDetection` encapsulent à la fois leurs données (seuils, configurations) et leurs comportements (méthodes de détection):

```python
class ThreatDetection:
    def __init__(self, threshold):
        self.threshold = threshold

    def detect_threats(self, ip_counts):
        threats = []
        for ip, count in ip_counts.items():
            if count > self.threshold:
                threats.append(ip)
                logging.info(f"Threat detected: {ip} sent {count} ICMP packets")
        return threats
```

Cette encapsulation permet de:
- Maintenir ensemble les données et les méthodes qui les manipulent
- Simplifier l'interface externe des composants
- Protéger l'état interne des composants

#### 2. Instanciation avec configurations différentes

L'approche orientée objet permet l'instanciation de plusieurs détecteurs avec des configurations différentes:

```python
# Deux détecteurs avec des seuils différents
standard_detector = ThreatDetection(threshold=50)
sensitive_detector = ThreatDetection(threshold=20)
```

Cela offre une flexibilité dans le déploiement, particulièrement utile dans un environnement conteneurisé où différents conteneurs peuvent avoir des paramètres adaptés à leur contexte.

#### 3. Testabilité améliorée

L'OOP facilite les tests unitaires en permettant d'isoler chaque composant:
- Les classes peuvent être instanciées et testées indépendamment
- Les dépendances peuvent être facilement simulées (mock)
- Les scénarios de test sont plus clairs et ciblés

#### 4. Extensibilité

Le modèle orienté objet facilite l'extension future du système:
- De nouvelles stratégies de détection peuvent être ajoutées en créant de nouvelles classes
- L'héritage peut être utilisé pour spécialiser les détecteurs existants
- Les interfaces communes simplifient l'intégration de nouveaux composants

Par exemple, on pourrait facilement étendre le système avec une classe `AdvancedThreatDetection` qui hériterait de `ThreatDetection` tout en ajoutant des fonctionnalités supplémentaires.

#### 5. Cohérence avec l'écosystème Python

L'approche OOP s'aligne avec de nombreuses bibliothèques Python utilisées dans le projet:
- Scapy utilise des classes pour représenter les paquets
- Le module logging utilise des classes pour les handlers et formatters
- PyClamd expose une interface orientée objet

Cette cohérence permet une intégration naturelle avec l'écosystème Python et ses bibliothèques.

### Structures de données choisies

#### Dictionnaires
1. **IP Counts (`defaultdict` → `dict`)** dans `capture_icmp_packets`:
   ```python
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
   ```
   - **Utilisation**: Comptage des paquets ICMP par adresse IP source
   - **Justification**: Le `defaultdict` simplifie l'incrémentation des compteurs sans vérification préalable d'existence, puis la conversion en `dict` standard offre une interface cohérente pour les fonctions appelantes
   - **Avantages**: Accès rapide en O(1) et association directe IP → compteur

2. **Résultat d'analyse de malware** dans `analyze_file`:
   ```python
   return {
       "is_malware": is_malware,
       "hash": file_hash
   }
   ```
   - **Utilisation**: Représentation des résultats d'analyse de fichiers
   - **Justification**: Structure flexible permettant d'ajouter facilement des attributs supplémentaires à l'avenir
   - **Avantages**: Format lisible et facile à sérialiser pour stockage ou transmission

#### Listes
1. **Liste des menaces** dans `detect_threats`:
   ```python
   threats = []
   for ip, count in ip_counts.items():
       if count > self.threshold:
           threats.append(ip)
           logging.info(f"Threat detected: {ip} sent {count} ICMP packets")
   ```
   - **Utilisation**: Collection des adresses IP identifiées comme menaces
   - **Justification**: Structure ordonnée simple pour collecter les résultats
   - **Avantages**: Facile à parcourir et à transformer en chaîne formatée pour la journalisation

2. **Handlers de logging** dans `main.py`:
   ```python
   handlers=[
       logging.FileHandler("network_log.txt"),
       logging.StreamHandler()
   ]
   ```
   - **Utilisation**: Configuration multiple des gestionnaires de journalisation
   - **Justification**: Collection ordonnée des handlers pour l'enregistrement simultané dans un fichier et sur la console
   - **Avantages**: Permet l'ajout facile de nouveaux handlers

#### Tuples
1. **Adresse IP et port** dans `get_container_ip`:
   ```python
   s.connect(("8.8.8.8", 80))
   ip = s.getsockname()[0]
   ```
   - **Utilisation**: Paire (adresse, port) pour la connexion socket et extraction de l'adresse IP
   - **Justification**: Utilisation de l'API socket standard qui retourne un tuple
   - **Avantages**: Structure de données immutable appropriée pour des valeurs qui ne changent pas

### Flux de données et algorithmes

#### Flux de données principal
1. **Capture des paquets ICMP**:
   - Entrée: Interface réseau, durée de capture
   - Traitement: Filtrage des paquets ICMP, comptage par IP source
   - Sortie: Dictionnaire {IP source: nombre de paquets}

2. **Détection des menaces**:
   - Entrée: Dictionnaire {IP source: nombre de paquets}, seuil de menace
   - Traitement: Comparaison des compteurs au seuil
   - Sortie: Liste des IPs dépassant le seuil

3. **Capture et analyse de fichier**:
   - Entrée: Interface réseau, durée de capture
   - Traitement: Capture et fusion des paquets TCP en fichier
   - Sortie: Chemin du fichier capturé

4. **Détection de malware**:
   - Entrée: Chemin du fichier
   - Traitement: Analyse ClamAV, calcul de hachage SHA256
   - Sortie: Dictionnaire {is_malware: bool, hash: string}

### Environnement de déploiement et tests

Le projet Bobbi The Watchdog est déployé sur des conteneurs Docker Alpine personnalisés, créant un environnement léger et optimisé pour la surveillance réseau. Les conteneurs sont configurés sur une plage d'adresses IP spécifique pour permettre une surveillance distribuée.

#### Infrastructure de test

L'environnement de test comprend plusieurs composants:

1. **Test de DDoS avec `flood.sh`**:
   ```bash
   #!/bin/zsh
   # Check if IP address is provided
   if [ -z "$1" ]; then
       echo "Usage: $0 <target_ip> [thread_count]"
       echo "Example: $0 192.168.1.1 10"
       exit 1
   fi
   
   TARGET_IP=$1
   THREADS=${2:-5}  # Default to 5 threads if not specified
   PING_COUNT=1000  # Number of pings per thread
   ```
   - **Utilisation**: Script de test qui simule une attaque par inondation ICMP
   - **Structures de données**: Utilisation de variables shell pour configurer les paramètres de test

2. **Serveur HTTPS pour tests de malware**:
   ```python
   import http.server
   import ssl
   import os

   PORT = 4443
   SERVE_DIR = "TEST_FILES"

   # Save current directory to load certs later
   BASE_DIR = os.path.abspath(os.getcwd())

   # Change working directory to serve TEST_FILES content
   os.chdir(SERVE_DIR)
   ```
   - **Utilisation**: Serveur HTTPS pour tester la détection de fichiers malveillants
   - **Structures de données**: Variables pour la configuration et chemins de fichiers

#### Adaptation au conteneur Docker

La configuration dans `config.py` est adaptée spécifiquement aux conteneurs Alpine:

```python
INTERFACE = "eth1"         # Interface réseau spécifique au conteneur Alpine
CAPTURE_DURATION = 20      # Durée optimisée pour l'environnement containerisé
THREAT_THRESHOLD = 50      # Seuil adapté aux tests avec flood.sh
```

Cette configuration permet de tester efficacement les fonctionnalités de capture de paquets et de détection de menaces dans un environnement qui reproduit des conditions réelles d'utilisation.

### Optimisations des structures de données

1. **Utilisation de `defaultdict`**:
   - Optimise le comptage des paquets par IP en évitant les vérifications d'existence
   - Réduit la verbosité du code et améliore la lisibilité

2. **Utilisation de dictionnaires pour les résultats**:
   - Permet d'étendre facilement les attributs des résultats sans modifier les signatures de fonction
   - Facilite la sérialisation pour la journalisation ou le stockage

3. **Utilisation d'une liste pour les menaces**:
   - Structure simple et efficace quand l'ordre n'est pas significatif
   - Performance d'insertion en O(1) adaptée au scénario de collecte de menaces

### Diagramme conceptuel du flux de données

```
[Configuration] ───────┐
                      │
                      ▼
[Interface Réseau] → [Capture Paquets ICMP] → [Dictionnaire IP→Compteur] → [Détection Menace] → [Liste Menaces]
                      │
                      ├──→ [Capture Paquets TCP] → [Assemblage Fichier] → [Analyse Malware] → [Dictionnaire Résultat]
                      │                                                       │
                      └─────────────────────────────────────────────────────→ [Journalisation]
```

### Considérations de conception futures

1. **Structures de données pour persistance**:
   - Stockage des résultats historiques dans une base de données
   - Utilisation de séries temporelles pour l'analyse de tendances

2. **Structures pour traitement parallèle**:
   - Files de travail pour le traitement asynchrone des paquets capturés
   - Dictionnaires concurrents pour le comptage parallèle

3. **Optimisation mémoire**:
   - Pour les environnements à ressources limitées, envisager des compteurs à fenêtre glissante
   - Filtrage précoce des paquets non pertinents

4. **Adaptation à l'environnement conteneurisé**:
   - Optimisation des structures pour les conteneurs Alpine avec ressources limitées
   - Partage de données entre conteneurs via des structures sérialisables
