#!/bin/bash

# Default values for environment variables
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-user}
DB_PASSWORD=${DB_PASSWORD:-password}
DB_NAME=${DB_NAME:-mydatabase}

# Example of waiting for PostgreSQL to become available (adjust as needed for your DB)
until PGPASSWORD=$DB_PASSWORD pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT to become available..."
  sleep 2
done
echo "PostgreSQL is available"

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# Start your Django app
exec "$@"