#!/usr/bin/python

from __future__ import print_function
import os
import subprocess
import sys
from datetime import datetime

BACKUP_DIR = os.environ["BACKUP_DIR"]
AWS_S3_PATH = os.environ["AWS_S3_PATH"]
DB_NAME = os.environ["DB_NAME"]
DB_PASS = os.environ["DB_PASS"]
DB_USER = os.environ["DB_USER"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.getenv("DB_PORT", 5432))
KEEP_BACKUP_DAYS = int(os.getenv("KEEP_BACKUP_DAYS", 7))

dt = datetime.now()
file_name = DB_NAME + "_" + dt.strftime("%Y-%m-%d") + '.sql'
backup_file = os.path.join(BACKUP_DIR, file_name)

if not AWS_S3_PATH.endswith("/"):
    AWS_S3_PATH = AWS_S3_PATH + "/"


def cmd(command):
    try:
        subprocess.check_output([command], shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        sys.stderr.write("\n".join([
            "Command execution failed. Output:",
            "-"*80,
            e.output,
            "-"*80,
            ""
        ]))
        raise


def backup_exists():
    return os.path.exists(backup_file)


def take_backup():
    """
    Trigger postgres-backup
    """
    cmd('env PGPASSWORD={0} pg_dump --format plain -c --host {1} --port {2} -U {3} {4} > {5}'
        .format(DB_PASS, DB_HOST, DB_PORT, DB_USER, DB_NAME, backup_file))


def upload_backup():
    """
    Upload to Amazon S3 Bucket
    """
    cmd("aws s3 cp %s %s" % (backup_file, AWS_S3_PATH))


def prune_local_backup_files():
    cmd("find %s -type f -prune -mtime +%i -exec rm -f {} \;" % (BACKUP_DIR, KEEP_BACKUP_DAYS))


def log(msg):
    print("[%s]: %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))


def main():
    start_time = datetime.now()
    log("Dumping database")
    take_backup()
    log("Uploading to S3")
    upload_backup()
    log("Pruning local backup copies")
    prune_local_backup_files()
    log("Backup complete, took %.2f seconds" % (datetime.now() - start_time).total_seconds())


if __name__ == "__main__":
    try:
        main()
        sys.exit(0)  # Success
    except Exception as e:
        raise e

