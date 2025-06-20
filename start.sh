#!/bin/bash
# start.sh - Railway startup script with multiple approaches

echo "🚂 Railway Startup Script"
echo "Setting environment variables for Railway deployment..."

# Set environment variables explicitly
export HOST="0.0.0.0"
export PORT="${PORT:-8000}"
export UVICORN_HOST="0.0.0.0"
export UVICORN_PORT="${PORT:-8000}"

echo "HOST: $HOST"
echo "PORT: $PORT"
echo "UVICORN_HOST: $UVICORN_HOST"
echo "UVICORN_PORT: $UVICORN_PORT"

# Try different approaches to start the server

echo "🔄 Approach 1: Try direct uvicorn server..."
if python uvicorn_server.py; then
    echo "✅ Direct uvicorn approach worked!"
else
    echo "❌ Direct uvicorn approach failed, trying main.py..."
    echo "🔄 Approach 2: Try main.py with forced environment..."
    
    # Run the Python server
    exec python main.py
fi