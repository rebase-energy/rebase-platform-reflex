# Reflex app Dockerfile for Fly.io
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including Node.js
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Initialize the Reflex app (development mode only)
RUN reflex init

# Make startup script executable
RUN chmod +x /app/start.sh

# Expose port
EXPOSE 3000

# Set environment variables for Vite host binding (development mode)
ENV REFLEX_ENV_MODE=dev
ENV HOST=0.0.0.0
ENV VITE_HOST=0.0.0.0
ENV VITE_ALLOWED_HOSTS=rebase-platform.fly.dev,localhost,127.0.0.1

# Run the startup script
CMD ["/app/start.sh"]
