# Bank Money Manager 

## 1. Overview

The project is a console application in Python for managing user account balances of a mock bank through PostgreSQL. Unlike the description in the assignment, the testing setup is built around an existing peewee ORM model rather than "raw" `psycopg2`. The project consists of the following files:

- `db.py` - responsible only for the database connection and the ORM model.
- `account_service.py` - the `AccountService` class, containing all banking business logic and accepting a connection as a parameter (which makes it easy to test).
- `main.py` - the CLI interface: reads `sys.argv`, validates input, and calls into `AccountService`.
- `fill_data.py` - populates the database with random test accounts.
- `conftest.py` - shared pytest fixtures (database connection, table creation, table cleanup, service instance, funded accounts).
- `test_main.py` - the tests themselves, organized into classes.

**Deviations from the assignment description:** the test file is named `test_main.py` rather than `test_bank.py`, as stated in step 1 of the instructions; accordingly, the business-logic source file is named `account_service.py` rather than `bank.py`, and there was no separate refactoring of a `bank.py` file - the CLI was written directly on top of an already-existing `AccountService`.

## 2. Technologies Used and Why

| Technology | Why it was chosen |
|---|---|
| **peewee** (`playhouse.postgres_ext.PostgresqlExtDatabase`) | A lightweight ORM that maps the `accounts` table (the `Money` model) to a Python class; provides a convenient `atomic()` context for the money-transfer transaction. |
| **psycopg2** (implicitly, via peewee) | The PostgreSQL driver required by peewee for `PostgresqlExtDatabase` to work. |
| **mimesis** | Generation of realistic test data (random names, UK locale) in `fill_data.py`. |
| **pytest** | A framework for writing isolated tests with fixtures (`conftest.py`). |
| **Decimal** | Used for all monetary amounts instead of `float`, to avoid rounding errors; transfer amounts are rounded to 2 decimal places. |

## 3. Architecture

### 3.1 db.py

Responsible purely for persistence:

- **db** - a `PostgresqlExtDatabase` connected to the `Money` database on `localhost:5432` with the `bank` user's credentials.
- **BaseModel / Money** - an ORM model with fields `id` (auto-increment), `owner` (unique text field), and `balance` (a `DecimalField` with the constraint `balance >= 0.0`).
- **init_db()** - opens the connection and creates the `Money` table if it doesn't already exist (`safe=True`).

### 3.2 account_service.py

The `AccountService` class encapsulates the banking logic. Its constructor takes a database connection, so the same class is used both by the CLI and by the tests. Its methods:

- **create_account(owner, balance=0)** - creates an account and returns its `id`; the amount is cast to `Decimal`.
- **get_balance(account_id)** - returns the balance, or raises `ValueError` if the account isn't found.
- **transfer(from_id, to_id, amount)** - atomically transfers funds between accounts. Raises `ValueError` for a non-positive amount, a missing account, or insufficient funds. Uses peewee's `connection.atomic()` so both balance updates succeed or fail together.
- **get_all_accounts()** - returns a list of all accounts, ordered by `id`.
- **get_account(account_id)** - an internal helper that fetches a single account or raises `ValueError` (catching `peewee.DoesNotExist`).

### 3.3 main.py

The CLI interface. The `Account` class holds static methods that parse `sys.argv`, validate types, and delegate calls to a shared `AccountService`. Validation and business-logic errors are converted into a custom `RuntimeError` class, which immediately prints a message and exits the process (`sys.exit(1)`). Supported commands:

- `transaction <from_id> <to_id> <amount>` - transfer funds.
- `status` - print the table of all accounts and balances.
- `get <id>` - print a single account's balance.
- `create_account <owner> <balance>` - create a new account (handling `peewee.IntegrityError` if the owner already exists).
- `fill-data` - populate the database with random test accounts.

`main()` initializes the database via `init_db()` and dispatches on `sys.argv[1]`, handling a missing or unknown command with a clear message.

### 3.4 fill_data.py

Uses `mimesis.Person` (UK locale) to generate 10 random names and random balances between 1 and 1000, creating a new account for each via `AccountService.create_account`. Duplicate owners (`peewee.IntegrityError`) are silently skipped.

### 3.5 conftest.py - Test Fixtures

- **db_connection** (scope=`session`) - enables `autocommit = True` and connects to the database before the whole test session.
- **create_tables** (scope=`session`, autouse=`True`) - creates the `Money` table once.
- **clean_tables** (autouse=`True`) - clears the `Money` table before **and** after every test.
- **service** - an `AccountService` instance ready for use in tests.
- **funded_accounts** - creates two accounts ("Alice" - 1000, "Bob" - 500) and returns their `id`s.

The implementation fully matches the fixture structure described in the assignment.

### 3.6 test_main.py - The Tests

- **TestCreateAccount** - creating an account with the default balance (0) and with an initial balance.
- **TestGetBalance** - retrieving the balance of an existing account, and checking that a `ValueError` is raised for a nonexistent account.
- **TestTransfer** - a successful transfer (checking both balances), transferring all funds (balance = 0), a transfer with insufficient balance (exception + balances unchanged), a negative-amount transfer (exception), a transfer from a nonexistent account (exception), a transfer to a nonexistent account (exception), and multiple consecutive transfers (checking the final balances).

All scenarios required by the assignment are implemented; each test class corresponds to one `AccountService` method.

## 4. How to Run It

Start PostgreSQL (e.g. via Docker Compose):
```bash
docker-compose up
```

Install dependencies:
```bash
pip install pytest peewee psycopg2-binary mimesis
```

Run the test suite:
```bash
pytest -v
```

Run the application:
```bash
python3 main.py fill-data
python3 main.py create_account <name> <balance>
python3 main.py status
python3 main.py get <id>
python3 main.py transaction <from_id> <to_id> <amount>
```

## 5. DB Connect

```bash
docker compose exec db psql -U bank -d Money -h localhost -p 5432
```

## 6. Sources

- [Peewee docs](http://docs.peewee-orm.com/)
- [Mimesis docs](https://mimesis.name/master/index.html)
- [Pytest docs](https://docs.pytest.org/)

> [!NOTE]
> I didn't want to do unit tests manually, so I paid [Hermes Agent](https://hermes-agent.nousresearch.com/) $0.07805 )
