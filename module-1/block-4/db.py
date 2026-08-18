import sys
from decimal import Decimal

import peewee
from playhouse.postgres_ext import *

db = PostgresqlExtDatabase(
    'Money',
    user='bank',
    password='password',
    host='localhost',
    port=5432,
)

class BaseModel(Model):
    class Meta:
        database = db

class Money(BaseModel):
    id = PrimaryKeyField()
    owner = TextField(unique=True)
    balance = DecimalField(default=0, constraints=[peewee.Check('balance >= 0.0')])

def init_db():
    db.connect()
    db.create_tables([Money], safe=True)

def transaction_db(from_id, to_id, amount):
    try:
        from_money = Money.get(Money.id == from_id)
        to_money = Money.get(Money.id == to_id)
    except Money.DoesNotExist:
        print("Transaction failed: no such account")
        sys.exit(1)

    if from_money.balance < amount:
        print("Transaction failed: not enough money")
        sys.exit(1)

    amount = Decimal(str(amount))

    from_money.balance -= amount
    to_money.balance += amount
    from_money.save()
    to_money.save()

def status_db():
    print("Banking system — Selector0073")
    print(f"{'ID':<4} | {'Name':<12} | {'Balance':>8}")
    print("-" * 30)
    for row in Money.select().order_by(Money.id):
        print(f"{row.id:<4} | {row.owner:<12} | {round(row.balance, 2):>8}")

def add_account_db(owner, balance):
    try:
        Money.create(owner=owner, balance=balance)
    except IntegrityError:
        print("Account already exists")
        sys.exit(1)