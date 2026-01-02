#!/bin/bash
# Start script for Fly.io deployment - SIMPLE INTEGRATED APPROACH
set -e

echo "=== Starting Reflex Deployment ==="
echo "Python: $(python --version)"
echo "Node: $(node --version)"
echo "Reflex: $(reflex --version)"

# Initialize Reflex
echo "Initializing Reflex..."
reflex init

# Apply hydration warning fix
if [ -f "/app/.web/app/_document.js" ]; then
    echo "Applying hydration warning fix..."
    sed -i 's/jsx("body",{})/jsx("body",{"suppressHydrationWarning":true})/' /app/.web/app/_document.js 2>/dev/null || true
fi

# Modify the generated Vite config to allow external hosts (don't override completely)
if [ -f "/app/.web/vite.config.ts" ]; then
    echo "Modifying Vite config to allow external hosts..."
    # Add allowedHosts to the server config without breaking the rest
    sed -i 's/server: {/server: { allowedHosts: ["rebase-platform.fly.dev", "localhost", "127.0.0.1"], /' /app/.web/vite.config.ts
elif [ -f "/app/.web/vite.config.js" ]; then
    echo "Modifying Vite JS config..."
    sed -i 's/server: {/server: { allowedHosts: ["rebase-platform.fly.dev", "localhost", "127.0.0.1"], /' /app/.web/vite.config.js
fi

# Set environment variables for host binding
export HOST=0.0.0.0
export VITE_HOST=0.0.0.0
export PORT=3000

# Start Reflex with both frontend and backend on the same port
echo "Starting Reflex with frontend and backend on same port..."
exec reflex run \
    --env prod \
    --single-port \
    --loglevel info
