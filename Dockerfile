FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (iputils for ping)
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY watchdog-agent.py .

# Make executable
RUN chmod +x watchdog-agent.py

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Run agent
CMD ["python3", "watchdog-agent.py"]
