#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Navigating to Django project directory"
cd opencodehub

echo "==> Running database migrations"
python manage.py makemigrations
python manage.py migrate --noinput

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Build complete"