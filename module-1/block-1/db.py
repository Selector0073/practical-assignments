from peewee import *
from playhouse.postgres_ext import *
import datetime

db = PostgresqlExtDatabase('Weather', user='weather', password='', host='localhost', port=5432)

class BaseModel(Model):
    class Meta:
        database = db

class Weather(BaseModel):
    time = DateTimeField(default=datetime.datetime.now)
    temperature = FloatField()


def init_db():
    db.connect()
    db.create_tables([Weather], safe=True)

def add_data(temperature):
    Weather.create(temperature=temperature)

def list_data():
    for weather in Weather.select().order_by(Weather.time.desc()):
        print(f"<{weather.time}> <{weather.temperature}°C> \n---")