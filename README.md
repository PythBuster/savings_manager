# Savings Manager

Savings Manager is an intuitive app designed to help you efficiently manage your savings. With virtual moneyboxes, you can allocate budgets for various financial goals, automate your savings strategy, and easily transfer funds between moneyboxes.

Set a fixed monthly savings amount to determine how much can be saved across all moneyboxes each month. The app automatically distributes this amount based on your preset priorities, ensuring that more important goals are reached faster. Additionally, if you withdraw from a moneybox, the system intelligently adjusts to prioritize refilling it, keeping your savings plan on track.

Savings Manager simplifies the process, allowing you to watch as your moneyboxes gradually fill up. You can also transfer funds between moneyboxes or make manual deposits at any time, giving you full control over your financial journey.

## Deployment / Contribution

### Docker
**NOTE**: You need a `.env` with all environments in `/envs` dir (see section **Env**).

1. Navigate to the Docker directory: `cd docker`
2. Run: `docker compose up -d` to start the PostgreSQL database and the Savings Manager app.  
   The app will be accessible at: `localhost:8000`

   - SwaggerUI: `localhost:64000/docs`
   - Sphinx: `localhost:64000/sphinx`

To get the latest version of the repository, simply pull it and rebuild the Docker container:  
`docker compose up --build`

### Manually

#### Poetry

[Poetry](https://python-poetry.org/) is used as the deployment and dependency manager.

##### Linux (Ubuntu 22.04):
1. Install Python 3.12 on your OS and add Python 3.12 to PATH.
2. Install pipx: `sudo apt update && sudo apt install pipx`
3. Install Poetry: `python3.12 -m pipx install poetry`
4. Install project dependencies:  
   ```bash
   cd PROJECT_ROOT
   poetry install



##### Database
A PostgreSQL database is required. To connect to the database, add a `.env` file in `/src/envs` with the following information:

##### Env
```
ENVIRONMENT=prod|dev|test

DB_DRIVER=postgresql+asyncpg
DB_NAME=savings_manager

DB_HOST=     [YOUR_HOSTADDRESS]
DB_PORT=     [YOUR_POSTGRES_DB_PORT]
DB_USER=     [YOUR_POSTGRES_DB_USER]
DB_PASSWORD= [YOUR_POSTGRES_DB_PASSWORD]


# smtp - the outgoing SMTP email server data
# -> SMTP_METHOD: only STARTTLS and TLS supported
SMTP_SERVER=
SMTP_PORT=
SMTP_METHOD=
SMTP_USER_NAME=
SMTP_PASSWORD=
```

Example:
```
ENVIRONMENT=prod

DB_DRIVER=postgresql+asyncpg
DB_NAME=savings_manager
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres

# smtp - the outgoing SMTP email server data
# -> SMTP_METHOD: only STARTTLS and TLS supported
SMTP_SERVER=
SMTP_PORT=
SMTP_METHOD=
SMTP_USER_NAME=
SMTP_PASSWORD=
```
The SMTP settings will be explained later.

The ENVIRONMENT variable in .env file will deactivate the uvicorn access logs, if value is set to: prod.
All other values will activate the access logs.

`uvicorn "main:app" [--no-access-log]`

`uvicorn.run("...", ... , access_log=False|True)`

###### SqlAlchemy (ORM)
We will use SQLAlchemy to manage and access the SQL database.

To create and migrate the database tables, use Alembic with the following command:
From the project root directory:
`poetry run alembic upgrade head`

**Note: The database must be reachable.**

## CI/CD

[GitHub Workflows](https://github.com/PythBuster/savings_manager/actions/new) is uses as CI/CD pipeline.

[Github Action](https://github.com/PythBuster/savings_manager/actions/new) Items:
- poetry build --> TODO
- pytest check --> TODO
- codestyle check --> TODO

## Code Documentation
Based on docstrings, sphinx will generate function documentation.

### Usage:

#### 1. Create rst Files base on current project:

In dir: `../sphinx` use command: `sphinx-apidoc -f -o source/ ../../src`

#### 2. Create HTML documentation:

In dir: `../sphinx` use command: `sphinx-build source build`

For detailed description, see: [Generating documentation from docstring using Sphinx](https://stackoverflow.com/questions/63486612/generating-documentation-from-docstring-using-sphinx)

An update sphinx documentation bash script is located in dir `script/`.
It will automatically update the sphinx documentation.


## DEV

### Alembic (Migration)


#### Init:
In our case, alembic already exists and don't need to be initialized.
Just for documentation: `alembic init -t async alembic` in project root dir will initialize an alembic environment.

#### Migration:
**Upgrade to a revision:**

*head (latest revision):* `alembic upgrade head`

*specific revision*: `alembic upgrade revision_id`

**Downgrade to a revision:**

*specific revision*: `alembic downgrade revision_id`

*specific revision (relative)*: `alembic downgrade head-1`

**Create new migration:**

`alembic revision --autogenerate -m "Added account table"`

# RUN

## .env file:We will use SqlAlchemy to manage and access the SQL database. 

To create and migrate the database tables, you need to use alembic 
by using the command:
In project root dir `poetry run alembic upgrade head`

**Hint**: The database must be reachable.
Savings Manager v2 is able to email you after automated savings is done.

If you want to receiver an email you have to use your email outgoing SMTP server, so the app will be able to send you an email.
You can obtain the outgoing SMTP email server data from your provider.

To use the email sender of the app, you need to add the smtp data in `/envs/.env`, like:

```# smtp - the outgoing SMTP email server data
# -> SMTP_METHOD: only STARTTLS and TLS supported
SMTP_SERVER=smtp.web.com
SMTP_PORT=465
SMTP_METHOD=STARTTLS
SMTP_USER_NAME=your.email@address.com
SMTP_PASSWORD=your-email-password
```

**Note: make sure that only you have access to your .env file !!!** 

## Run savings manager in python environment:
If poetry environment is initialized and all dependencies are initially installed
via:
- for production (usage only): `poetry install --without dev`
- for development: `poetry install`

you should be able to start the app from root directory of the project by using the following command:
`poetry run python -m src.main`


This will start a service on:
`http://localhost:64000`

To see the API documentation or use the API via SwaggerUI, visit:
`http://localhost:64000/docs`


## Run savings manager as docker:
ou can start the Savings Manager as a Docker container. After cloning the main repository and adding/adapting your `.env` file in `savings_manager/envs/`, you will be able to start the Docker service using the following command:

Navigate to `savings_manager/docker` and run:
`docker compose up --build -d` 
This will rebuild your container if necessary and start the container as a daemon (in the background).

Alternatively you can use the `START_SAVINGS_MANAGER.sh` script to start the savings manager into as a Docker container:
Navigate to `savings_manager/scripts` and run:
`./START_SAVINGS_MANAGER.sh`

(in windows, run the .bat file)

The savings manager into the docker will run on port 8001 and you will reach the service at: http://localhost:8001

API documentation: http://localhost:64000/docs
Code documentation: http://localhost:64000/sphinx

## Bug-Report:
Please join my discord (https://discord.gg/PyqQhJ2d34).
You can send me bug reports on the following discord text channel: 🐞-bugs-savings-manager


Enjoy! :)

