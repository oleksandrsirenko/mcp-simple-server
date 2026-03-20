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

# Set environment for production
# PORT is set by Railway at runtime; default 8000 is in main.py
ENV HOST=0.0.0.0

# Run the server directly with Python
CMD ["python", "main.py"]