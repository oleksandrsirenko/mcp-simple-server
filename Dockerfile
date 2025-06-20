FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install -e .

# Create non-root user for security
RUN adduser --disabled-password --gecos "" mcpuser && \
    chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose port
EXPOSE 8000

# Set environment for production - these should be explicitly set
ENV HOST=0.0.0.0
ENV PORT=8000

# Health check with Railway's expected port
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://0.0.0.0:${PORT}/mcp/ -X POST \
    -H "Content-Type: application/json" \
    -H "MCP-Protocol-Version: 2025-06-18" \
    -H "Accept: application/json, text/event-stream" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"health-check","version":"1.0"}}}' || exit 1

# Run the server with explicit environment variables
CMD ["sh", "-c", "HOST=0.0.0.0 PORT=${PORT:-8000} python main.py"]