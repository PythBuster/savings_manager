#!/bin/bash
echo "Sleep for 10 seconds... wait for Database..."
sleep 10s

poetry run alembic upgrade head
exec "$@"