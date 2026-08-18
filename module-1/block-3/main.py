from db import init_db, add_data, list_data
from http import HTTPStatus
import requests
import time, sys

URL = "https://api.open-meteo.com/v1/forecast?latitude=50.7472&longitude=25.3254&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,rain,weather_code,wind_speed_10m,wind_direction_10m&timezone=Europe%2FKyiv"

def service():
    while True:
        r = requests.get(URL)
        data = r.json()
        if r.status_code != 200:
            print(f"Error: {HTTPStatus(r.status_code)}")
            sys.exit(1)
        print(data["current"]["temperature_2m"], data["current"]["relative_humidity_2m"])
        add_data(data["current"]["temperature_2m"], data["current"]["relative_humidity_2m"])
        time.sleep(60)

def history():
    print("Weather history from: Selector0073") # Name is confidential information
    list_data()

def main():
    dispatch = {
        "service": service,
        "history": history,
    }

    init_db()

    try:
        parameter = sys.argv[1]
    except IndexError:
        print("Missing parameter")
        sys.exit(1)

    try:
        dispatch[parameter]()
    except KeyError:
        print(f"Unknown parameter: {parameter}")
        sys.exit(1)

if __name__ == "__main__":
    main()