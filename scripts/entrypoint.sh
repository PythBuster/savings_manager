#!/bin/bash
echo "Sleep for 10 seconds... wait for Database..."
sleep 10s

/root/.local/share/pipx/venvs/poetry/bin/poetry run alembic upgrade head
exec "$@"