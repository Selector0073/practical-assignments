from peewee import *
import datetime

db = SqliteDatabase("db.sqlite3")

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
    for weather in Weather.select():
        print(f"<{weather.time}> <{weather.temperature}°C> \n---")