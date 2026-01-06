# Dockerfile for Railway Deployment
# Uses Python 3.12 and installs dependencies from backend/requirements.txt

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy backend directory
COPY backend/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Railway will set PORT env var)
EXPOSE $PORT

# Start command
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
