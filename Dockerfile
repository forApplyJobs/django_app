FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=project.settings

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
        netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories with proper permissions
RUN mkdir -p media/frames media/outputs logs \
    && chmod 755 media media/frames media/outputs logs

# Create and set permissions for entrypoint
RUN echo '#!/bin/bash\n\
echo "Waiting for database..."\n\
while ! nc -z db 5432; do\n\
  sleep 0.1\n\
done\n\
echo "Database started"\n\
\n\
echo "Waiting for Redis..."\n\
while ! nc -z redis 6379; do\n\
  sleep 0.1\n\
done\n\
echo "Redis started"\n\
\n\
echo "Creating log directory and setting permissions..."\n\
mkdir -p /app/logs\n\
chmod 755 /app/logs\n\
\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput --clear\n\
\n\
echo "Creating superuser if not exists..."\n\
python manage.py shell << EOF\n\
from django.contrib.auth import get_user_model\n\
User = get_user_model()\n\
if not User.objects.filter(username="admin").exists():\n\
    User.objects.create_superuser("admin", "admin@example.com", "admin123456")\n\
    print("Superuser created: admin/admin123456")\n\
else:\n\
    print("Superuser already exists")\n\
EOF\n\
\n\
echo "Starting server..."\n\
exec "$@"' > /entrypoint.sh

RUN chmod +x /entrypoint.sh

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set ownership of all app files to appuser
RUN chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Use entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "project.asgi:application"]
