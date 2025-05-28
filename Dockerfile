FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    clamav \
    clamav-daemon \
    clamav-freshclam \
    clamav-unofficial-sigs \
    tcpdump \
    libpcap-dev \
    gcc \
    libc6-dev \
    linux-headers-generic \
    bash \
    curl \
    tar \
    netcat \
    iproute2 \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Install uv using the install script
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN chmod +x /uv-installer.sh && \
    bash /uv-installer.sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx && \
    rm /uv-installer.sh && \
    echo "uv installed. Checking version:" && \
    /usr/local/bin/uv --version

# Set up ClamAV - Ubuntu version
RUN mkdir -p /var/run/clamav && \
    chown clamav:clamav /var/run/clamav && \
    chmod 755 /var/run/clamav && \
    mkdir -p /var/lib/clamav && \
    chown clamav:clamav /var/lib/clamav && \
    chmod 755 /var/lib/clamav && \
    mkdir -p /var/log/clamav && \
    chown clamav:clamav /var/log/clamav && \
    chmod 755 /var/log/clamav

# Create app directory
WORKDIR /app

# Copy application files
COPY . /app/

# Copy ClamAV configuration
COPY clamd.conf /etc/clamav/clamd.conf

# Create and activate virtual environment using uv
# Use the full path to uv to ensure it's found
RUN /usr/local/bin/uv venv
ENV PATH="/app/.venv/bin:${PATH}"

# Install the package in development mode
RUN /usr/local/bin/uv pip install -e .

# Update ClamAV virus definitions (this might take a while)
RUN freshclam || echo "ClamAV freshclam warning - will retry at runtime"

# Ensure ClamAV socket directory exists and is accessible
RUN mkdir -p /var/run/clamav && \
    chown clamav:clamav /var/run/clamav && \
    chmod 755 /var/run/clamav

# Setup entry point script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Network capabilities
# Note: The container must be run with --cap-add=NET_ADMIN and --net=host
# or with a specific network interface exposed

# Set entry point
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
