FROM python:3.11

LABEL maintainer="PythBuster <pythbuster@gmail.com>"

RUN apt update && apt install git curl

RUN python3.11 -m pip install pipx
RUN python3.11 -m pipx install poetry

RUN git clone https://github.com/PythBuster/savings_manager.git
RUN cd savings_manager
WORKDIR /savings_manager

ARG POETRY_PATH=/root/.local/share/pipx/venvs/poetry/bin/poetry
RUN $POETRY_PATH install
RUN $POETRY_PATH run python3.11 -c "from src import utils; utils.create_envfile_from_envvars();"

CMD ["/root/.local/share/pipx/venvs/poetry/bin/poetry", "run", "python3.11", "./src/main.py", "--environment", "dev"]
