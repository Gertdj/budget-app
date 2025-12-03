FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port (will be overridden by PORT env var in production)
EXPOSE 8000

# Use PORT environment variable if available, otherwise default to 8000
CMD gunicorn budget_app.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120
