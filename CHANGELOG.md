# CHANGELOG.md

## x.y.z (unreleased)
...

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
