# Savings Manager


## Deployment / Contribution
### poetry

[Poetry](https://python-poetry.org/) is used as deploymentd and dependency manager.

#### Usage: 

### Database
 

#### SqlAlchemy (ORM)
We will use SqlAlchemy to manage and access the SQL database. 

##### Usage: 
Part of alembic, no direct use.

#### Alembic (Migration)


##### Usage: 
###### Init:
In our case, alembic already exists and don't need to be initialized.
Just for documentation: `alembic init -t async alembic` in project root dir will initialized an alembic environment.

###### Migration:
**Upgrade to a revision:**

*head (latest revision):* `alembic upgrade head`

*specific revision*: `alembic upgrade revision_id`

**Downgrade to a revision:**

*specific revision*: `alembic downgrade revision_id`

*specific revision (relative)*: `alembic downgrade head-1`

**Create new migration:**

`alembic revision --autogenerate -m "Added account table"`


### CI/CD

[GitHub Workflows](https://github.com/PythBuster/savings_manager/actions/new) is uses as CI/CD pipeline.

[Github Action](https://github.com/PythBuster/savings_manager/actions/new) Items:
- poetry build --> TODO
- pytest check --> TODO
- codestyle check --> TODO