from mimesis import Person
from mimesis.locales import Locale
import random
from db import add_account_db

def fill_random_data():
    person = Person(Locale.UK)

    for _ in range(10):
        name = person.first_name()
        money = random.randint(1, 1000)
        add_account_db(name, money)
