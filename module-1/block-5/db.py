import peewee
from playhouse.postgres_ext import *

db = DatabaseProxy()

class BaseModel(Model):
    class Meta:
        database = db

class Money(BaseModel):
    id = PrimaryKeyField()
    owner = TextField(unique=True)
    balance = DecimalField(default=0, constraints=[peewee.Check('balance >= 0.0')])

def init_db(status):
    if status:
        database = SqliteDatabase(':memory:')
    else:
        database = PostgresqlExtDatabase(
            'Money',
            user='bank',
            password='password',
            host='localhost',
            port=5432,
        )

    db.initialize(database)
    db.connect()
    db.create_tables([Money], safe=True)

class DataBase:
    @staticmethod
    def transaction(acc1, acc2, almount):
        acc1_db = Money.get(Money.id == acc1)
        acc2_db = Money.get(Money.id == acc2)
        acc1_db.balance -= almount
        acc2_db.balance += almount
        acc1_db.save()
        acc2_db.save()

    @staticmethod
    def create(owner, balance=0):
        Money.create(owner=owner, balance=balance)

    @staticmethod
    def get_all_accounts():
        return Money.select().order_by(Money.id)

    @staticmethod
    def get_by_id(id):
        return Money.get(Money.id == id)