#!/bin/sh

# Build and run Bobbi the Watchdog in a Docker container

# Ensure our entrypoint script is executable
echo "Making docker-entrypoint.sh executable..."
chmod +x docker-entrypoint.sh

echo "Building Bobbi the Watchdog container..."
docker-compose build

echo "Starting Bobbi the Watchdog container..."
docker-compose up -d

echo "Container is now running. To check the logs, run:"
echo "docker-compose logs -f"

echo "To access the container, run:"
echo "docker-compose exec bobbi-watchdog bash"

echo "Container IP address:"
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' bobbi-watchdog
