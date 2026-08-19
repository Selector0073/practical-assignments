import random
import peewee
from db import db
from account_service import AccountService

def fill_random_data():
    from mimesis import Person
    from mimesis.locales import Locale

    person = Person(Locale.UK)
    service = AccountService(db)

    for _ in range(10):
        try:
            name = person.first_name()
            money = random.randint(1, 1000)
            service.create_account(name, money)
        except peewee.IntegrityError:
            pass
