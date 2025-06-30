#!/usr/bin/env bash

# Entry script for Render deployment
echo "Starting Gunicorn..."
gunicorn order_service.wsgi:application