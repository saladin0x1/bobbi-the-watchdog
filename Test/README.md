# Répertoire de Tests pour Bobbi the Watchdog

Ce répertoire contient les outils et fichiers nécessaires pour tester les fonctionnalités de Bobbi the Watchdog.

## Structure des Fichiers

### 📜 flood.sh
Script shell pour tester la détection des attaques DDoS. Ce script simule une attaque par inondation ICMP en envoyant de multiples pings vers une cible spécifique.

**Utilisation:**
```bash
./flood.sh <ip_cible> [nombre_threads]
# Exemple: ./flood.sh 192.168.1.1 10
```

### 🌐 https-server.py
Serveur HTTPS simple pour tester la détection de malwares. Ce serveur permet de servir des fichiers de test via HTTPS sur le port 4443.

**Fonctionnalités:**
- Sert les fichiers du répertoire `TEST_FILES`
- Utilise SSL/TLS pour les connexions sécurisées
- Port par défaut: 4443

### 📁 certs/
Répertoire contenant les certificats SSL/TLS pour le serveur HTTPS:
- `cert.pem`: Certificat SSL auto-signé
- `key.pem`: Clé privée pour le certificat SSL

### 📁 test_file/
Répertoire contenant les fichiers de test pour la détection de malwares:
- `eicar.com.txt`: Fichier de test standard EICAR pour valider la détection de malwares

## Configuration

Les certificats SSL sont configurés pour localhost et sont auto-signés. Pour les environnements de production, il est recommandé d'utiliser des certificats valides émis par une autorité de certification reconnue.

## Notes de Sécurité

⚠️ Ces outils sont destinés uniquement aux tests dans un environnement contrôlé. Ne pas utiliser `flood.sh` contre des systèmes non autorisés, car cela pourrait être considéré comme une attaque DDoS malveillante.
