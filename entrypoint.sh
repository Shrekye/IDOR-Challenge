#!/bin/sh
set -e

python3 seed_db.py

flask run --host=0.0.0.0 --port=5000
