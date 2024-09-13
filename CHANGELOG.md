# CHANGELOG.md

## x.y.z (unreleased)

## 2.19.1 (2024-09-13)
### Fixes:
- added cached function to get the env settings
- fix: conftest.py and load .env.test
- fix: tests

## 2.19.0 (2024-09-13)
### Changes:
- implement decorator for BackgroundTaskRunner to be able to decorate task function by
  setting specific sleeping time

## 2.18.0 (2024-09-13)
### Changes:
- fix: AppEnvVariables wrongly loaded settings from ENVIRONMENT instead of .env file
- updated docstring for endpoints and class __init__ functions

## 2.17.0 (2024-09-11)
### Feature:
- adapt docker compose file by using healthstates for postgres_database and test database services
- expose savings manager (docker service: app) on port 64000
- update README.md

## 2.16.0 (2024-09-11)
### Feature:
- update sphinx documentation and mount/route sphinx documentation in inside vueJS statics

## 2.15.0 (2024-09-09)
### Feature:
- added /app/metadata endpoint

## 2.14.0 (2024-09-09)
### Changed:
- simplified/unified endpoint response codes
- adapt request/exception handler
- adapt custom openapi handler (fastapi)

## 2.13.1 (2024-09-09)
### Changed:
- fix: added missing poetry dependency
- updated poetry dependencies

## 2.13.0 (2024-09-09)
### Changed:
- added slowapi dependency and limited send-testemail endpoint to 1 request per minute

## 2.12.0 (2024-09-08)
### Changed:
- mount vueJS static dir to app root "/" and deploy vueJS UI 
    note: (without static files inside, need manual export of static files from vueJS to this directory)

## 2.11.0 (2024-09-07)
### Changed:
- unify pydantic models
- unify usage of app states in endpoints

## 2.10.0 (2024-09-07)
### Changed:
- update poetry dependencies

## 2.9.0 (2024-09-07)
### Changed:
- performance: add httptools as dependency to boost up uvicorns http parsing

## 2.8.1 (2024-09-07)
### Changed:
- fix: check name against None before stripping/trimming string (update moneybox data)

## 2.8.0 (2024-09-06)
### Changed:
- adapt json schemas (pydantic models): respect JSON naming convention and return/accept camel-cased keys in JSON data
- make pydantic models strict: accept strict types and use validators for names (disallow leading/trailing whitespaces)

## 2.7.0 (2024-09-04)
### Changed:
- adapt /prioritylist endpoints by adding "total" in response data

## 2.6.1 (2024-09-04)
### Changed:
- performance: adapt /prioritylist endpoints and let fastAPI implicitly cast return data

## 2.6.0 (2024-09-02)
### Changed:
- performance: added uvloop dependency and use uvloop
- performance: deactivate uvicorn access logs for production mode (environment)
- performance: small optimizations in endpoint returns

## 2.5.1 (2024-09-02)
### Changed:
- small design changes in automated savings email html

## 2.5.0 (2024-09-01)
### Changed:
- send multipart (plain+html) emails for automated savings report

## 2.4.0 (2024-09-01)
### Changed:
- adapt GET/UPDATE prioritylist endpoint: return prioritylist sorted by priority

## 2.3.1 (2024-09-01)
### Changed:
- Fix: write correct mode in transaction log description for overflow moneybox

## 2.3.0 (2024-08-29)
### Changed:
- remove priority from create/update moneybox
- add new moneyboxes at the end of the priority list
- reset/refresh priority numbers by keeping priority order if moneybox is deleted

## 2.2.2 (2024-08-29)
### Changed:
- update code documentation (sphinx)
- change docker container app port to 64000
- update README.md

## 2.2.1 (2024-08-27)
### Changed:
- use own app logger to avoid logging SQLAlchemy transaction logs

## 2.2.0 (2024-08-27)
### Changed:
- remove app settings id from /settings endpoints, currently there are only one app settings instance in database

## 2.1.0 (2024-08-27)
### Feature:
- added send testmail endpoint

## 2.0.1 (2024-08-27)
### Changed:
- protect enabling email receiving if smtp settings in .env are missing
- fix tests
- update README.md by adding a description for app start and SMTP settings (.env file)

## 2.0.0 (2024-08-27)
### Changed:
- fix docker compose app service, so savings manager can run into a docker container

## 1.21.0 (2024-08-27)
### Features:
- setup global logger and write exceptions in ../src/errors.log

## 1.20.0 (2024-08-26)
### Features:
- send email after automated savings scheduled (if flag is enabled for receiving emails in app settings)

## 1.19.2 (2024-08-19)
### Changes:
- clean code and update fastapi & uvicorn dependencies

## 1.19.1 (2024-08-19)
### Changes:
- fix automated savings algorithm

## 1.19.0 (2024-08-18)
### Features:
- implement modes for overflow moneybox for automated savings

### Changes:
- refactor db functions for automated savings distribution

## 1.18.0 (2024-08-18)
### Features:
- added overflow_moneybox_automated_savings_mode column to AppSettings table # db migration

### Changes:
- adapted pydantic request/response models for AppSettings
- adapted unit tests

## 1.17.0 (2024-08-17)
### Features:
- added automated_savings_logs_table and log actions like: automated saving, app settings change

## 1.16.0 (2024-08-17)
### Features:
- implement automated savings logic and scheduler, that runs every hour on the 1st of month
  (note: the automated savings scheduler does not check whether the task has already been completed for the day,
  it will run on every hour for now, this will be resolved in next app versions).

## 1.15.0 (2024-08-16)
### Changes:
- remove automated_trigger_day from app settings

## 1.14.0 (2024-08-16)
### Features:
- add app settings table
- implement app settings db functions
- implement app settings endpoints

### Changes:
- adapt test data generation: allow excluding tables in truncate progress

## 1.13.0 (2024-08-15)
### Changes:
- adapt priority list GET+PATCH endpoints: remove overflow moneybox from request/response data

## 1.12.0 (2024-08-14)
### Features:
- add priority list GET+PATCH endpoints

### Changes:
- adapt tests, replace some and add further tests, incl. tests for priority list endpoints

## 1.11.0 (2024-08-13)
### Features:
- add priority list db get/update function

## 1.10.0 (2024-08-13)
### Changes:
- change pytest ordering dependency (use pytest-order instead of pytest-ordering)

## 1.9.0 (2024-08-13)
### Changes:
- refactor db core functions
- fix: moved setting priority of moneybox to None in correct db function

## 1.8.1 (2024-08-13)
### Changes:
- adapt docker build pipelines

## 1.8.0 (2024-08-13)
### Changes:
- adapt some unit tests to avoid unexpected behavior like different order of records into database as expected

## 1.7.0 (2024-08-13)
### Features:
- switch database to postgres

## 1.6.0 (2024-08-07)
### Features:
- adapt create moneybox endpoint: handle constraints errors for priority
- adapt update moneybox endpoint: protect updating overflow moneybox and handle constraints errors
- adapt delete moneybox endpoint: protect deleting overflow moneybox
- get moneyboxes will detect double or missing overflow moneybox and will raise an InconsistentDatabase Exception

## 1.5.0 (2024-08-06)
### Features:
- protect deleting overflow moneybox (which is flagged by priority=0)

## 1.4.0 (2024-08-06)
### Features:
- add v2 related columns to moneybox table
- switch database from postgres to sqlite
- adapt and implement further unit tests

## 1.3.0 (2024-08-03)
### Features:
- add note column to all tables to be able to add admin notes to each record

## 1.2.0 (2024-08-03)
### Changes:
- redesign and implementation of a new test architecture
- add further tests to reach a test coverage over 90%

## 1.1.0 (2024-05-03)
### Changes:
- add counterparty_moneybox_name to transactions table in database
- add min len check-constraint for counterparty_moneybox_name if set
- add balance check-constraint to moneyboxes table (balance >= 0)
- performance optimization: resolving counterparty_moneybox_name ins transaction_logs will not be called dynamically anymore

## 1.0.0 (2024-05-03)
### Changes:
- fix divers bugs
- reduce db migration scripts (breaking change!) NOTE: v1.0.0 is not compatible to older databases!
- clean code
- case insensitivity for moneybox names


## 0.8.0 (2024-04-01)

### Changes:
- simplify /balance/-add, -sub and -transfer endpoints
- reduce transaction log data in request data

## 0.7.0 (2024-03-31)

### Fixes:
- prevent updating moneybox name with existing name


## 0.6.0 (2024-03-31)

### Changes:
- add counterparty_moneybox_name in transaction logs data

## 0.5.0 (2024-03-31)

### Changes:
- check moneybox id existence before validation request data in endpoints

## 0.4.1 (2024-03-31)

### Changes:
- prevent deleting moneyboxes with a balance > 0

## 0.4.0 (2024-03-31)

### Features:
- add transaction logs for deposit, withdraw and transfer

## 0.3.0 (2024-02-27)

### Features:
- add deposit, withdraw and transfer balance endpoints for moneyboxes


## 0.2.0 (2024-02-21)

### Features:
- add CRUD DB functionality for moneyboxes
- add CRUD endpoints to handle with moneyboxes
- add first DB migration
