FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create logs directory
RUN mkdir -p /app/logs

# Set Python path
ENV PYTHONPATH=/app

# Run the application with gunicorn for Cloud Run
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 src.main_cloudrun:app
