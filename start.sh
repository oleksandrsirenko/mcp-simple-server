#!/bin/bash
# start.sh - Railway startup script

echo "Railway Startup Script"
echo "Setting environment variables for Railway deployment..."

# Set environment variables explicitly
export HOST="0.0.0.0"
export PORT="${PORT:-8000}"

echo "HOST: $HOST"
echo "PORT: $PORT"
echo "Starting MCP server..."

# Run the Python server
exec python main.py