#!/bin/bash

poetry run alembic upgrade head

exec "$@"