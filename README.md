# Savings Manager

The "Savings Manager" helps you to manage your savings. With the help of virtual accounts, budgets can be saved for various goals, and this is completely automated.

By setting a fixed monthly savings amount, you can determine the maximum monthly amount that can be saved in the overall system. By assigning desired savings amounts for each moneybox and upper savings limits, the monthly savings amount is automatically distributed across the moneyboxes at the beginning of each month. By setting a fixed priority, you can achieve a savings constellation that helps you achieve certain savings goals faster than others.

The strength here: if you withdraw a certain amount from a cash box, the priority list of cash boxes will automatically create a balance that ensures that this just emptied cash box is quickly refilled.

This makes it easy to save and you can watch as each moneybox is gradually refilled. Of course, amounts can be moved between the moneyboxes and manual deposits into the moneyboxes are always possible!

Translated with DeepL.com (free version)

## Deployment / Contribution

### Docker
1. jump into docker dir: `cd docker`
2. call: `docker compose up -d` to run postgres and savings_manager app
App will be exposed to: `localhost:8000`

SwaggerUI: `localhost:8000/docs`
Sphinx: `localhost:8000/sphinx`

To get the newest repo, just pull it and rebuilt docker:
`docker compose up --build`

### Manually
#### poetry

[Poetry](https://python-poetry.org/) is used as deployment and dependency manager.

##### Linux (Ubuntu 22.04):
1. Install python 3.11 on your OS and add python 3.11 to PATH
2. Install pipx: `sudo apt update && sudo apt install pipx`
3. Install poetry: `pipx install poetry --python 311`
4. Install project dependencies:
   `cd PROJECT_ROOT`
   `poetry install`



##### Database
A postgres database is needed. To connect to the database, add a `.env` file
in: `/src/envs` with following information:

```
DB_DRIVER=postgresql+asyncpg
DB_NAME=savings_manager

DB_HOST=     [YOUR_HOSTADDRESS]
DB_PORT=     [YOUR_POSTGRES_DB_PORT]
DB_USER=     [YOUR_POSTGRES_DB_USER]
DB_PASSWORD= [YOUR_POSTGRES_DB_PASSWORD]
```

Example:
```
DB_DRIVER=postgresql+asyncpg
DB_NAME=savings_manager
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
```


###### SqlAlchemy (ORM)
We will use SqlAlchemy to manage and access the SQL database. 

To create and migrate the database tables, you need to use alembic 
by using the command:
In project root dir `poetry run alembic upgrade head`

**Hint**: The database must be reachable.

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

If poetry environment is initialized and all dependencies are initially installed
via:
- for production (usage only): `poetry install --without dev`
- for development: `poetry install`

you should be able to start the app from root directory of the project by using the following command:
`poetry run python -m src.main`


This will start a service on:
`http://localhost:8001`

To see the API documentation or use the API via SwaggerUI, visit:
`http://localhost:8001/docs`

``