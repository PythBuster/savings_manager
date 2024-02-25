#!/bin/bash

/root/.local/share/pipx/venvs/poetry/bin/poetry run alembic upgrade head
exec "$@"