#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Waiting for PostgreSQL at $DOJO_DB_HOST:$DOJO_DB_PORT..."

while ! nc -z "$DOJO_DB_HOST" "$DOJO_DB_PORT"; do
  sleep 0.1
done

echo "PostgreSQL is available"

mkdir -p /app/dojo/logs
chmod -R 777 /app/dojo/logs

# Run create migrations
python manage.py makemigrations

# Run Django migrations
python manage.py migrate --noinput

# Collect static files (optional)
python manage.py collectstatic --noinput

# Start the Django server
python manage.py runserver 0.0.0.0:8000

# Load dummy data
python manage.py create_dataset

# Execute the command specified as arguments to this script
exec "$@"
