#!/bin/bash
set -e

# Execute backup
python3 /backup/backup.py

exec "$@"
