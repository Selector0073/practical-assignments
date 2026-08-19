import peewee
from playhouse.postgres_ext import PostgresqlExtDatabase, Model

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
    id = peewee.AutoField()
    owner = peewee.TextField(unique=True)
    balance = peewee.DecimalField(
        default=0,
        constraints=[peewee.Check('balance >= 0.0')],
    )


def init_db():
    db.connect()
    db.create_tables([Money], safe=True)
