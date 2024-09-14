## Docker Compose:
Further service `postgres_database_backup` will be used to create database dumps by using `pg_dump`



## Backup creation
`
In `postgres_database_backup`docker two cronjobs will handle database backup.

One each 12 hours will create a backup, the second one (provided as clean up script in /scripts) will remove all backup fies and keep last 3.

To define the backup directory, adapt `volume` in `docker-compose.yml` for the docker sevice `postres_database_backup`:

```
volumes:  
  - /ADAPT-PATH:/postgres_backup
```
