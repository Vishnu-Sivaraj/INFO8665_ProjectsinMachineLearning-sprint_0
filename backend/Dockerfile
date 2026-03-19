# ============================================================
# INSIGHT-311 Backend — Flask API + ML Pipeline
# ============================================================
FROM python:3.10-slim

# Install system dependencies for psycopg2, audio processing, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory (mirrors the repo root so imports like
# `from src.database.database import ...` work unchanged)
WORKDIR /app

# Copy and install Python dependencies first (Docker layer caching)
# Uses requirements-docker.txt which excludes Windows-only packages
COPY requirements-docker.txt /app/requirements-docker.txt
RUN pip install --no-cache-dir -r requirements-docker.txt

# Download the spaCy NLP model
RUN python -m spacy download en_core_web_md

# Copy backend source code
COPY backend/ /app/backend/

# Copy data & model directories (training data, saved models)
COPY data/      /app/data/
COPY ml_models/ /app/ml_models/
COPY config/    /app/config/

# The .env file is injected at runtime via docker-compose (env_file)
# so we do NOT bake credentials into the image.

# Expose Flask port
EXPOSE 8311

# Start the Flask API server
CMD ["python", "backend/src/api/ml_service.py"]
