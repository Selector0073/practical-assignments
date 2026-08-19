import pytest
from db import db, Money
from account_service import AccountService

@pytest.fixture(scope="session")
def db_connection():
    db.autocommit = True
    db.connect()
    yield db
    db.close()

@pytest.fixture(scope="session", autouse=True)
def create_tables(db_connection):
    db.create_tables([Money], safe=True)

@pytest.fixture(autouse=True)
def clean_tables(db_connection):
    Money.delete().execute()
    yield
    Money.delete().execute()

@pytest.fixture
def service(db_connection):
    return AccountService(db_connection)

@pytest.fixture
def funded_accounts(service):
    acc1 = service.create_account("Alice", 1000)
    acc2 = service.create_account("Bob", 500)
    return acc1, acc2
