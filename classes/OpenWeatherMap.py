import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv
from pytz import timezone
import datetime
from .googleMap import latlng_to_postal_code
from .kakasi import do_conv2
import json

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
API_KEY = os.environ.get("OW_ID")
ZIP = '{},JP'
API_URL_rain = 'http://api.openweathermap.org/data/2.5/forecast?zip={0}&units=metric&lang=ja&APPID={1}'
API_URL_weather = "http://api.openweathermap.org/data/2.5/weather?units=metric&q={city}&APPID={key}"


def get_weather_forecast(lat, lng):
    url = API_URL_rain.format(ZIP.format(latlng_to_postal_code(lat + "," + lng)), API_KEY)
    response = requests.get(url)
    print(url)
    base = {}
    sort = []
    forecastData = response.json()
    for item in forecastData['list']:
        forecastDatetime = timezone(
            'Asia/Tokyo').localize(datetime.datetime.fromtimestamp(item['dt']))
        weatherDescription = item['weather'][0]['description']
        temperature = item['main']['temp']
        rainfall = 0
        if 'rain' in item and '3h' in item['rain']:
            rainfall = item['rain']['3h']
        base[forecastDatetime] = '{0}, {1}℃, {2}mm'.format(
            weatherDescription, temperature, rainfall)
        sort.append(forecastDatetime)
    return [base, sort]


def get_weather(city_name):
    url = API_URL_weather.format(city=do_conv2(city_name), key=API_KEY)
    response = requests.get(url)
    data = response.json()
    # jsonText = json.dumps(data, indent=4)
    return data
