FROM python:3.11

LABEL maintainer="PythBuster <pythbuster@gmail.com>"

RUN apt-get update && apt-get install -y --no-install-recommends python3-poetry python3-dev

COPY src /savings_manager/src
COPY scripts /savings_manager/scripts
COPY docs/sphinx /savings_manager/docs/sphinx
COPY alembic /savings_manager/alembic
COPY alembic.ini /savings_manager/alembic.ini
COPY poetry.lock /savings_manager/poetry.lock
COPY pyproject.toml /savings_manager/pyproject.toml
COPY README.md /savings_manager/README.md

RUN mkdir /savings_manager/envs

WORKDIR /savings_manager

ENV PYTHONPATH="${PYTHONPATH}:/src"

RUN poetry install --without dev
RUN poetry run python3.11 -c "from src import utils; utils.create_envfile_from_envvars();"

ENTRYPOINT ["sh", "scripts/entrypoint.sh"]
CMD ["poetry", "run", "python3.11", "-m", "src.main", "--environment", "live"]
