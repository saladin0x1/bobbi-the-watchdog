#!/bin/sh
set -e

# Initialize and update ClamAV virus database if needed
echo "Initializing ClamAV..."
if [ ! -f /var/lib/clamav/main.cvd ]; then
    echo "ClamAV database not found. Running freshclam..."
    freshclam
fi

# Start the ClamAV daemon
echo "Starting ClamAV daemon..."
clamd &

# Wait for ClamAV socket to become available
echo "Waiting for ClamAV to start..."
while [ ! -S /var/run/clamav/clamd.sock ]; do
    echo "Waiting for ClamAV socket..."
    sleep 1
done
echo "ClamAV is ready."

# Create required directories if they don't exist
mkdir -p /app/captured_files

# Print container IP for debugging
echo "Container IP information:"
ip addr

# Ensure virtual environment is activated and run the watchdog application
echo "Starting Bobbi the Watchdog..."
export PATH="/app/.venv/bin:$PATH"
exec watchdog
