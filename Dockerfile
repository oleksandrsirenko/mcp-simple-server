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

# Set environment for production
ENV HOST=0.0.0.0
ENV PORT=8000

# Run the server directly with Python
CMD ["python", "main.py"]