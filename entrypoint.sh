#!/bin/bash

echo "Running migrations..."
python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn order_service.wsgi:application --bind 0.0.0.0:$PORT
