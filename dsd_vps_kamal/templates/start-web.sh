#!/bin/sh
echo "Migrating database..."
python manage.py migrate --noinput

echo "Starting web server..."
python manage.py server web
