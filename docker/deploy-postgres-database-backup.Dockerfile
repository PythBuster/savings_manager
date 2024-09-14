FROM postgres:16

LABEL maintainer="PythBuster <pythbuster@gmail.com>"

# Install cron and bash
RUN apt-get update && apt-get install -y cron nano

# Create necessary directories for cron and backups
RUN mkdir /postgres_backup

COPY scripts/entrypoint_postgres_database_backup.sh /
COPY scripts/clean_up_postgres_database_backups.sh /

ENTRYPOINT ["sh", "/entrypoint_postgres_database_backup.sh"]
CMD ["cron", "-f"]