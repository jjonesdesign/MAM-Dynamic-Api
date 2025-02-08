#!/bin/bash

# Check if MAM_ID is provided
if [ -z "$1" ]; then
    echo "Error: MAM_ID not provided"
    echo "Usage: ./build_and_run.sh <mam_id>"
    exit 1
fi

# Get current user's UID and GID
USER_ID=$(id -u)
GROUP_ID=$(id -g)

# Stop and remove any existing container with the same name
docker stop mam-dynamic-api 2>/dev/null || true
docker rm mam-dynamic-api 2>/dev/null || true

# Build the Docker image
echo "Building Docker image..."
docker build -t mam-dynamic-api .

# Run the container with environment variable and volume mount
echo "Starting container..."
docker run --name mam-dynamic-api \
    -e MAM_ID="$1" \
    -v "$(pwd)/config:/config" \
    --user "${USER_ID}:${GROUP_ID}" \
    --log-driver json-file \
    --log-opt max-size=10m \
    --log-opt max-file=3 \
    mam-dynamic-api