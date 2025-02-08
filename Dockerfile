FROM python:3.9-slim

# Install curl
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create config directory for persistent data
RUN mkdir -p /config && \
    # Set permissions for /config directory
    chmod 777 /config

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create the cookies file if it doesn't exist
RUN touch /config/mam.cookies

# Set volume for persistent storage
VOLUME ["/config"]

CMD ["python", "main.py"] 