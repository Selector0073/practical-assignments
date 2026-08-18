from mimesis import Person
from mimesis.locales import Locale
import random, peewee
from db import DataBase

def fill_random_data():
    person = Person(Locale.UK)

    for _ in range(10):
        try:
            name = person.first_name()
            money = random.randint(1, 1000)
            DataBase.create(name, money)
        except peewee.IntegrityError:
            pass