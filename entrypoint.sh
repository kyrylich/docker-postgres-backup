#!/bin/bash
set -e

# Execute backup
python -u /backup/backup.py

exec "$@"
