# backend/Dockerfile
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies for Postgres and WeasyPrint
# (Using the corrected Debian 12 package name: libgdk-pixbuf-2.0-0)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

COPY . .

# Collect static files for Django Admin
RUN mkdir -p /app/static
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Run Gunicorn (Production Web Server)
CMD ["gunicorn", "inventory.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]