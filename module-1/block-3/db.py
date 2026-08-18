from peewee import *
from playhouse.postgres_ext import *
import psycopg2
import datetime

db = PostgresqlExtDatabase(
    'Weather',
    user='weather',
    password='weather',
    host='127.0.0.1',
    port=5432
)

class BaseModel(Model):
    class Meta:
        database = db

class Weather(BaseModel):
    time = DateTimeField(default=datetime.datetime.now)
    temperature = FloatField()
    humidity = FloatField()


def init_db():
    db.connect()

def add_data(temperature, humidity):
    Weather.create(temperature=temperature, humidity=humidity)

def list_data():
    for weather in Weather.select():
        print(f"<{weather.time}> <{weather.temperature}°C> <humidity {weather.humidity}%> \n---")