cd docker
test_env_file_path="./../envs/.env.test"
docker compose --env-file "$test_env_file_path" up --build -d --remove-orphans test_postgres_database --wait
