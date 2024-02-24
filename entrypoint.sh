#!/bin/bash

# Default values for environment variables
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-user}
DB_PASSWORD=${DB_PASSWORD:-password}
DB_NAME=${DB_NAME:-mydatabase}

timestamp() {
  date +"%T" # current time
}

# Example of waiting for PostgreSQL to become available (adjust as needed for your DB)
# until PGPASSWORD=$DB_PASSWORD pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
#   timestamp
#   echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT to become available..."
#   sleep 2
# done

timestamp
echo "PostgreSQL is available"

# Apply database migrations
timestamp
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

timestamp
echo "Collecting static files..."
python manage.py collectstatic --noinput
# Start your Django app

timestamp
echo "Entry point script executed successfully"
exec "$@"