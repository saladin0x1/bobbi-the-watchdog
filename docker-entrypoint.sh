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

# Wait for ClamAV socket to become available
echo "Waiting for ClamAV to start..."
SOCKET_PATHS="/var/run/clamav/clamd.ctl /var/run/clamav/clamd.sock"
TIMEOUT=30
COUNT=0
SOCKET_FOUND=""

while [ -z "$SOCKET_FOUND" ] && [ $COUNT -lt $TIMEOUT ]; do
    for SOCKET_PATH in $SOCKET_PATHS; do
        if [ -S "$SOCKET_PATH" ]; then
            SOCKET_FOUND="$SOCKET_PATH"
            break
        fi
    done
    
    if [ -z "$SOCKET_FOUND" ]; then
        echo "Waiting for ClamAV socket... ($COUNT/$TIMEOUT) Clamd process status:"
        pgrep clamd || echo "Clamd process not found."
        ls -l /var/run/clamav/ 2>/dev/null || echo "/var/run/clamav/ directory not found"
        sleep 2
        COUNT=$((COUNT + 1))
    fi
done

if [ -n "$SOCKET_FOUND" ]; then
    echo "ClamAV socket $SOCKET_FOUND is ready."
    ls -l "$SOCKET_FOUND"
else
    echo "WARNING: No ClamAV socket found after $TIMEOUT seconds."
    echo "Listing /var/run/clamav/ directory:"
    ls -lR /var/run/clamav/ 2>/dev/null || echo "/var/run/clamav/ directory not accessible"
    echo "Checking clamd process status:"
    ps aux | grep clamd
    echo "Checking clamd logs (if available):"
    if [ -f /var/log/clamav/clamd.log ]; then
        tail -20 /var/log/clamav/clamd.log
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
