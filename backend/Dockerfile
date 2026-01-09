FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will override with $PORT env var)
EXPOSE 8000

# Run uvicorn with production settings
# Note: Railway's startCommand in railway.toml will override this CMD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
