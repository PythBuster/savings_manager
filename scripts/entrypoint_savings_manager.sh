#!/bin/bash

poetry run alembic -x ENVIRONMENT=dev upgrade head

exec "$@"