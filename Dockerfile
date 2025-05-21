FROM alpine:latest

# Install required packages
RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    clamav \
    clamav-daemon \
    clamav-libunrar \
    tcpdump \
    libpcap-dev \
    gcc \
    python3-dev \
    musl-dev \
    linux-headers \
    libc-dev \
    bash \
    curl \
    tar

# Install uv using the install script
ADD https://astral.sh/uv/install.sh /uv-installer.sh
# Tell the installer where to put uv
# ENV UV_TOOL_BIN_DIR=/usr/local/bin # This doesn't seem to be respected by the installer
RUN chmod +x /uv-installer.sh && \
    bash /uv-installer.sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    mv /root/.local/bin/uvx /usr/local/bin/uvx && \
    rm /uv-installer.sh && \
    echo "uv installed. Checking version:" && \
    /usr/local/bin/uv --version

# Set up ClamAV
RUN mkdir -p /run/clamav && \
    chown clamav:clamav /run/clamav && \
    freshclam

# Create app directory
WORKDIR /app

# Copy application files
COPY . /app/

# Create and activate virtual environment using uv
# Use the full path to uv to ensure it's found
RUN /usr/local/bin/uv venv
ENV PATH="/app/.venv/bin:${PATH}"

# Install the package in development mode
RUN /usr/local/bin/uv pip install -e .

# Ensure ClamAV socket directory exists and is accessible
RUN mkdir -p /var/run/clamav && \
    chown clamav:clamav /var/run/clamav

# Setup entry point script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Network capabilities
# Note: The container must be run with --cap-add=NET_ADMIN and --net=host
# or with a specific network interface exposed

# Set entry point
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
