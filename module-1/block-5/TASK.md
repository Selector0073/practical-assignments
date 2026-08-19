## 0. Role

You are a senior Python developer responsible for refactoring a banking CLI application and writing a complete suite of automated tests. Your work will go through code review: the code must be production-grade, not just "working."

Below are the input project files, HARD rules that must not be violated, and detailed requirements for the final result. If any requirement in the **"Task"** section conflicts with the **"Mandatory Rules"** section, the **"Mandatory Rules"** section takes precedence.

---

## 1. Input Files

- `TASK.md` - the original task + overwrite rules
- `10-testing-practice.md` - course materials (source of the original requirements)
- `db.py` - the database access layer (Peewee, PostgreSQL)
- `account_service.py` - business logic (draft version, has issues - see section 6)
- `main.py` - CLI layer (draft version, has issues - see section 6)
- `fill_data.py` - test data seeding
- `conftest.py` - pytest fixtures (draft version)
- `test_main.py` - tests (draft version, incorrect file name - see section 6)

---

## 2. Mandatory Rules (Priority #1, must not be violated)

1. **Poetry** - the only way to manage dependencies and the virtual environment. No `pip install`, `requirements.txt`, or manually created `venv`. The project must have a correct `pyproject.toml` (+ `poetry.lock`) with `main` and `dev` dependency groups (pytest, etc. - in `dev`).
2. **Peewee** - the only ORM/database layer. No raw SQL/psycopg2 anywhere, except what is already encapsulated within Peewee.
3. **Preserve the current project structure**:
   - `db.py` is responsible **exclusively** for the database connection, model declarations, and low-level database operations (`connect`, `create_tables`, configuration). No business logic, CLI logic, or business-rule exception handling belongs here.
   - `main.py` is responsible for everything else: CLI, argument parsing, calling the service layer, printing to the console.
   - This rule takes priority over the `bank.py` structure mentioned in the course materials - the `main.py`/`db.py` file names must not be changed.

---

## 3. Target Project Structure

```
project/
├── pyproject.toml
├── poetry.lock
├── db.py                  # DB connection, Peewee models, init_db()
├── account_service.py     # AccountService - all business logic
├── main.py                # CLI (argparse), entry point, output formatting
├── fill_data.py           # Test data seeding (via AccountService)
├── conftest.py            # pytest fixtures
├── test_bank.py           # Tests (rename from test_main.py!)
└── README.md              # How to install (poetry install) and run (poetry run pytest)
```

---

## 4. General Python Code Requirements

- **Python 3.11+**, full type coverage (`Decimal`, `int`, `str`, `Optional[...]`, method return types).
- Every public method/class - a docstring (short description + `Args`/`Returns`/`Raises`).
- **Never shadow built-in names** (the `RuntimeError` class in the current `main.py` is a critical bug: it shadows the built-in exception and calls `sys.exit()` right inside `__init__`, which is an antipattern and breaks exception semantics). Use a custom `CLIError(Exception)` class with no side effects in the constructor; call `sys.exit()` **only** inside `main()`.
- **Monetary amounts must use `Decimal` only**, never `float`. The current `main.py` converts the balance via `round(float(sys.argv[3]), 2)` - this is a source of rounding errors. Fix it to convert the string directly to `Decimal`.
- Explicit error handling at layer boundaries: `AccountService` raises domain exceptions (`ValueError` or custom classes such as `AccountNotFoundError`, `InsufficientFundsError`, `InvalidAmountError` - pick one approach and be consistent), `main.py` catches them and formats a message for the user.
- No bare `except:`. Catch specific exceptions.
- Formatting - `black` + `ruff`/`flake8`, both as Poetry dev dependencies.
- No global mutable state outside the `db` connection.

---

## 5. Requirements for `AccountService` (`account_service.py`)

The class takes the **database connection as a constructor parameter** (already the case in the draft - keep it).

| Method | Contract |
|---|---|
| `create_account(owner: str, balance: Decimal \| int \| float = 0) -> int` | Creates an account, returns the `id`. Raises an exception on duplicate `owner` (uniqueness) - do not silently swallow `IntegrityError`, let it propagate for handling in `main.py`. |
| `get_balance(account_id: int) -> Decimal` | Returns the balance. Raises an exception if the account is not found. |
| `transfer(from_id: int, to_id: int, amount: Decimal) -> None` | Atomic transfer (`db.atomic()` - already implemented, keep it). Checks: `amount > 0`, `from_id != to_id` (add this - missing in the draft), sufficient funds, existence of both accounts. On error, no balance should change (the transaction must roll back). |
| `get_all_accounts() -> list[Money]` | Returns all accounts, ordered by `id` (already implemented). |

**Additional nuance to check:** if `from_id == to_id`, self-transfer must be explicitly forbidden (this case is missing both from the service and from the tests in the current code).

---

## 6. Issues Found in the Current Code (must be fixed)

1. `main.py`: the `RuntimeError(Exception)` class shadows the built-in, calls `print()` + `sys.exit(1)` inside `__init__` - remove it, replace with a custom `CLIError`, and keep `sys.exit` only inside `main()`.
2. `main.py`: `create_account` converts the balance via `float` instead of `Decimal` - fix to `Decimal(sys.argv[3])`.
3. `AccountService.transfer` does not forbid `from_id == to_id` - add a check and a test for this case.
4. `test_main.py` has the wrong name - it should be `test_bank.py` per the task.
5. `conftest.py`: `db.autocommit = True` is set before `db.connect()` - verify whether this actually affects `PostgresqlExtDatabase` (Peewee is autocommit by default outside `atomic()` anyway); if the line is unnecessary, remove it or document why it's there.
6. `fill_data.py` depends on `mimesis`, which is not listed in any dependency file - add it to Poetry (the `dev` group or `main`, depending on whether `fill-data` is a production CLI command).
7. No `pyproject.toml`/`poetry.lock` - create from scratch.
8. No tests for `get_all_accounts()` - TASK.md explicitly requires this service method, but no test covers it. Add `TestGetAllAccounts`.
9. No test that `create_account` with an existing `owner` raises an exception (unique constraint) - add a test.

---

## 7. Requirements for `conftest.py`

Fixtures (names must match TASK.md exactly - do not change):

- `db_connection` (`scope="session"`) - connection to the test PostgreSQL database, autocommit.
- `create_tables` (`scope="session"`, `autouse=True`) - creates the Peewee model table(s).
- `clean_tables` (`autouse=True`) - clears the table before **and** after each test (already implemented - keep the symmetry).
- `service` - an instance of `AccountService(db_connection)`.
- `funded_accounts` - creates 2 accounts (e.g., 1000 and 500), returns a tuple `(id1, id2)`.

The test database must be **separate** from the production one (e.g., via a `TEST_DATABASE_URL` environment variable or a separate configuration in `db.py`/`conftest.py` - do not hardcode production credentials in the test config).

---

## 8. Requirements for the Tests (`test_bank.py`)

The file **must** be named `test_bank.py` (not `test_main.py`).

Class/case structure - minimum:

```
TestCreateAccount
├── test_create_account_with_default_balance
├── test_create_account_with_initial_balance
└── test_create_account_with_duplicate_owner_raises   # NEW

TestGetBalance
├── test_get_balance_of_existing_account
└── test_get_balance_of_nonexistent_account

TestGetAllAccounts                                      # NEW CLASS
├── test_returns_all_created_accounts
└── test_returns_empty_list_when_no_accounts

TestTransfer
├── test_successful_transfer
├── test_transfer_all_funds
├── test_transfer_when_balance_insufficient
├── test_transfer_negative_amount
├── test_transfer_zero_amount                           # NEW (edge case)
├── test_transfer_from_nonexistent_account
├── test_transfer_to_nonexistent_account
├── test_transfer_to_same_account_raises                # NEW
└── test_multiple_consecutive_transfers
```

Each test:
- Uses only fixtures, no direct SQL/ORM calls in the test body, other than verification via `service.get_balance` / `service.get_all_accounts`.
- Compares amounts only via `Decimal("...")`, never via `float`.
- Checks exceptions via `pytest.raises(...)` with the most specific exception type possible (never a bare `Exception`).

---

## 9. Acceptance Criteria (Definition of Done)

- [ ] `poetry install` sets up the project without manual edits.
- [ ] `poetry run pytest -v` - all tests pass against a clean test PostgreSQL instance.
- [ ] `db.py` contains no business-logic or CLI code whatsoever.
- [ ] `main.py` never touches Peewee models directly - only through `AccountService`.
- [ ] No shadowing of built-in names.
- [ ] All monetary operations use `Decimal`; `float` is used nowhere for amounts.
- [ ] The test file is named `test_bank.py`.
- [ ] All cases from section 8 are covered, including the new edge cases.
- [ ] `pyproject.toml` lists all real dependencies (`peewee`, `psycopg2-binary`, `mimesis`, `pytest`) in the appropriate groups.
- [ ] README with Poetry-based run instructions.
