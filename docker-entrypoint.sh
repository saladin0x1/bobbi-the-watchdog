#!/bin/bash
set -e

# Initialize and update ClamAV virus database if needed
echo "Initializing ClamAV..."
if [ ! -f /var/lib/clamav/main.cvd ] && [ ! -f /var/lib/clamav/main.cld ]; then
    echo "ClamAV database not found. Running freshclam..."
    freshclam || echo "freshclam failed, but continuing..."
fi

# Ensure ClamAV directories have correct permissions
chown -R clamav:clamav /var/lib/clamav
chown -R clamav:clamav /var/log/clamav
chown -R clamav:clamav /var/run/clamav

# Check if clamd.conf exists
CLAMD_CONF="/etc/clamav/clamd.conf"
if [ ! -f "$CLAMD_CONF" ]; then
    echo "ERROR: ClamAV configuration file $CLAMD_CONF not found!" 
    exit 1
fi
echo "ClamAV configuration file $CLAMD_CONF found."

# Start the ClamAV daemon
echo "Starting ClamAV daemon..."
clamd &

# Wait for ClamAV socket to become available
echo "Waiting for ClamAV to start..."
SOCKET_PATH="/var/run/clamav/clamd.ctl"  # Updated to use .ctl socket
TIMEOUT=30 # Increased timeout for slower systems
COUNT=0

while [ ! -S "$SOCKET_PATH" ] && [ $COUNT -lt $TIMEOUT ]; do
    echo "Waiting for ClamAV socket at $SOCKET_PATH... ($COUNT/$TIMEOUT) Clamd process status:"
    pgrep clamd || echo "Clamd process not found."
    ls -l /var/run/clamav/
    sleep 2 # Increased sleep interval
    COUNT=$((COUNT + 1))
done

if [ -S "$SOCKET_PATH" ]; then
    echo "ClamAV socket $SOCKET_PATH is ready."
    ls -l "$SOCKET_PATH"
else
    echo "WARNING: ClamAV socket $SOCKET_PATH not found after $TIMEOUT seconds."
    echo "Listing /var/run/clamav/ directory:"
    ls -lR /var/run/clamav/
    echo "Checking clamd process status:"
    ps aux | grep clamd
    echo "Checking clamd logs (if available):"
    if [ -f /var/log/clamav/clamd.log ]; then
        cat /var/log/clamav/clamd.log
    else
        echo "/var/log/clamav/clamd.log not found."
    fi
    echo "Continuing startup, but ClamAV may not be functional."
fi

# Create required directories if they don't exist
mkdir -p /app/captured_files

# Print container IP for debugging
echo "Container IP information:"
ip addr

# Ensure virtual environment is activated and run the watchdog application
echo "Starting Bobbi the Watchdog..."
export PATH="/app/.venv/bin:$PATH"

# Try to run the watchdog, but keep container alive if it fails
if ! uv run watchdog; then
    echo "Watchdog failed to start. Keeping container alive for debugging..."
    echo "You can exec into the container to investigate the issue."
    tail -f /dev/null
fi
