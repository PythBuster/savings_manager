#!/bin/bash

# todo: instead of 'postgres_backup' use env var!
# keep last 3 backups and remove older backups
ls -1t /postgres_backup/backup_*.sql | tail -n +4 | xargs -r rm --