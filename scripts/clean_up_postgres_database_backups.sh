#!/bin/bash

# todo: instead of 'postgres_backup' use env var!
# keep last 3 backups and remove older backups
ls -1t /postgres_backup/* | tail -n +3 | xargs -r rm --