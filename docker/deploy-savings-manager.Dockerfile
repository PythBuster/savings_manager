FROM python:3.12

LABEL maintainer="PythBuster <pythbuster@gmail.com>"

RUN apt-get update && apt-get install -y --no-install-recommends python3-poetry python3-dev

COPY src /savings_manager/src
COPY temp /savings_manager/temp
COPY envs /savings_manager/envs
COPY scripts /savings_manager/scripts
COPY docs/sphinx /savings_manager/docs/sphinx
COPY static /savings_manager/static
COPY alembic /savings_manager/alembic
COPY alembic.ini /savings_manager/alembic.ini
COPY poetry.lock /savings_manager/poetry.lock
COPY pyproject.toml /savings_manager/pyproject.toml
COPY README.md /savings_manager/README.md

WORKDIR /savings_manager

ENV PYTHONPATH="${PYTHONPATH}:/src"

RUN poetry install --without dev

ENTRYPOINT ["sh", "scripts/entrypoint_savings_manager.sh"]
CMD ["poetry", "run", "python", "-m", "src.main"]
