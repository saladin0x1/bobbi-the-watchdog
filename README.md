# Bobbi the Watchdog

A network security tool for packet capture, threat detection, and malware analysis.

## Docker Container Setup

Bobbi the Watchdog can be run inside an Alpine Linux container, which provides isolation and a distinct IP address for network monitoring.

### Prerequisites

- Docker
- Docker Compose

### Building and Running

1. Clone this repository:

```bash
git clone https://github.com/saladin0x1/bobbi-the-watchdog.git
cd bobbi-the-watchdog
```

2. Make the run script executable:

```bash
chmod +x run_container.sh
```

3. Run the container:

```bash
./run_container.sh
```

This will build the container, start it in the background, and display its IP address.

### Container Capabilities

- The container runs with `NET_ADMIN` capability to allow packet sniffing
- It uses bridge networking mode to get its own distinct IP address
- ClamAV is preinstalled and runs automatically
- The application monitors network traffic on eth0 interface

### Viewing Logs

To view the application logs in real-time:

```bash
docker-compose logs -f
```

### Testing

The `Test` directory contains tools for testing the application:

1. Ping flood test:
```bash
# Get the container IP first
CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' bobbi-watchdog)
# Then run the flood test against a target
cd Test
./flood.sh $TARGET_IP 10
```

2. HTTPS malware test server:
```bash
cd Test
python https-server.py
```

Original repository: whoami.saladin0x1.ru 