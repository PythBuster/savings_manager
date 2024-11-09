cd ../docker
env_file_path="./../envs/.env.dev"
docker compose --env-file "$env_file_path" up --build -d --remove-orphans postgres_database --wait
