# Dockerfile for Railway Deployment
# Uses Python 3.12 and installs dependencies from backend/requirements.txt

FROM python:3.12-slim

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend directory
COPY backend/ /app/

# Copy startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Railway sets PORT environment variable dynamically
# Use startup script to handle PORT properly
CMD ["/app/start.sh"]
