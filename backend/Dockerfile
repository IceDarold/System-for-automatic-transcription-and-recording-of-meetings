FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script first and make it executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Copy the rest of the application
COPY . .

# Add current directory to PYTHONPATH
ENV PYTHONPATH=/app

# Create non-privileged user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Start the application
CMD ["/app/entrypoint.sh"] 