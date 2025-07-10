#!/bin/bash
set -e

# Wait for the DB to be ready
echo "Waiting for PostgreSQL..."
until pg_isready -h db -p 5432 -U "$POSTGRES_USER"; do
  sleep 1
done

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Start Django
echo "Starting server..."
exec "$@"
