#!/bin/bash
set -e

# Execute backup
python3 -u /backup/backup.py

exec "$@"
