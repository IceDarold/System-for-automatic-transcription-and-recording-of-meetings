FROM python:3.11-slim

WORKDIR /app

# Install system dependencies with retry mechanism and alternative mirrors
RUN echo "deb http://mirror.yandex.ru/debian/ bullseye main" > /etc/apt/sources.list && \
    echo "deb http://mirror.yandex.ru/debian/ bullseye-updates main" >> /etc/apt/sources.list && \
    echo "deb http://mirror.yandex.ru/debian-security bullseye-security main" >> /etc/apt/sources.list && \
    apt-get clean && \
    apt-get update --allow-releaseinfo-change && \
    apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Add current directory to PYTHONPATH
ENV PYTHONPATH=/app

# Create non-privileged user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Start the application
CMD ["/app/scripts/init_db.sh"] 