FROM python:3.12-slim

LABEL maintainer="PythBuster <pythbuster@gmail.com>"

# Install and set pipx binary path
RUN pip install --no-cache --upgrade pipx
ENV PATH="/root/.local/bin:$PATH"

# Install poetry via pipx
RUN pipx install poetry
RUN pipx ensurepath

# Create and the working directory
RUN mkdir /savings_manager
WORKDIR /savings_manager

# Copy dependencies first to take advantage of caching
COPY poetry.lock pyproject.toml /savings_manager/

# Now copy the rest of the code
COPY src /savings_manager/src
COPY temp /savings_manager/temp
COPY envs /savings_manager/envs
COPY scripts /savings_manager/scripts
COPY docs/sphinx /savings_manager/docs/sphinx
COPY static /savings_manager/static
COPY alembic /savings_manager/alembic
COPY alembic.ini /savings_manager/alembic.ini
COPY README.md /savings_manager/README.md

# Install dependencies without dev packages
RUN poetry install --no-root --without dev

# Set the Python path
ENV PYTHONPATH="${PYTHONPATH}:/savings_manager/src"

# Entrypoint and CMD
ENTRYPOINT ["sh", "scripts/entrypoint_savings_manager.sh"]
CMD ["poetry", "run", "python", "-m", "src.main"]
