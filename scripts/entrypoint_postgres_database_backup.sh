#!/bin/bash

# Create .pgpass \
echo "postgres_database:5432:${POSTGRES_DB}:${POSTGRES_USER}:${POSTGRES_PASSWORD}" > ~/.pgpass && \
    chmod 600 ~/.pgpass

# Create a script that runs pg_dump
echo "#!/bin/bash\n pg_dump --data-only -h postgres_database -p 5432 -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f ${BACKUP_DIR}/\$(date -Iminute).sql" > /backup.sh && \
    chmod +x /backup.sh

# Add cron job to crontab for root
echo "0 */12 * * * root /bin/bash /backup.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/postgres_backup && \
    chmod 0644 /etc/cron.d/postgres_backup

# Add cron job to crontab for root
echo "* 12 * * 7 root /bin/bash /clean_up_postgres_database_backups.sh >> /var/log/cron.log 2>&1" > /etc/cron.d/clean_postgres_backup && \
    chmod 0644 /etc/cron.d/clean_postgres_backup

exec "$@"