# --- AIWAF Dockerfile ---
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffering stdout (better container logs)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install OS-level build deps needed by scikit-learn / numpy wheels on slim images
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the actual project (see .dockerignore for what's excluded)
COPY . .

# Logs are written at runtime — make sure the dir exists and is writable
RUN mkdir -p logs

EXPOSE 5000

# Run with gunicorn instead of Flask's dev server (debug=True) for anything beyond local testing
CMD ["gunicorn", "--chdir", "app", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "waf_api:app"]
