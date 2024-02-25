FROM python:3.11

LABEL maintainer="PythBuster <pythbuster@gmail.com>"

RUN python3.11 -m pip install pipx
RUN python3.11 -m pipx install poetry

COPY src /savings_manager/src
COPY scripts /savings_manager/scripts
COPY docs/sphinx /savings_manager/docs/sphinx
COPY alembic /savings_manager/alembic
COPY alembic.ini /savings_manager/alembic.ini
COPY poetry.lock /savings_manager/poetry.lock
COPY pyproject.toml /savings_manager/pyproject.toml
RUN mkdir /savings_manager/envs

WORKDIR /savings_manager

ENV PYTHONPATH "${PYTHONPATH}:/src"

ARG POETRY_PATH=/root/.local/share/pipx/venvs/poetry/bin/poetry
RUN $POETRY_PATH install
RUN $POETRY_PATH run python3.11 -c "from src import utils; utils.create_envfile_from_envvars();"

ENTRYPOINT ["sh", "scripts/entrypoint.sh"]
CMD ["/root/.local/share/pipx/venvs/poetry/bin/poetry", "run", "python3.11", "-m", "src.main", "--environment", "dev"]
