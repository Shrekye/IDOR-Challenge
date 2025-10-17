#!/bin/sh
set -e

python3 seed_db.py

exec gunicorn -b 0.0.0.0:5000 app:app --workers=1
