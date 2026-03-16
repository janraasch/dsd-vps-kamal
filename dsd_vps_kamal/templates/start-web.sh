#!/bin/sh
echo "Migrating database..."
python manage.py migrate --noinput

echo "Starting web server..."
gunicorn --bind :8000 --workers 2 {{ django_project_name }}.wsgi
