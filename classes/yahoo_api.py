import os
import requests
from os.path import join, dirname
from dotenv import load_dotenv
import feedparser
from bs4 import BeautifulSoup
import discord

dotenv_path = join(dirname(__file__), '../../sigma.env')
load_dotenv(dotenv_path)
app_id = os.environ.get("APP_ID")

geocoder_base = "https://map.yahooapis.jp/geocode/V1/geoCoder?appid={app_id}&query={query}&output={type}"
weather_information_base = "https://map.yahooapis.jp/weather/V1/place?appid={app_id}" \
                           "&coordinates={coordinates}&output={type}"
reader = "https://map.yahooapis.jp/map/V1/static?appid" \
         "={app_id}&lat=39&lon=139.730&z=6&width=500&height=500&overlay=type:rainfall|datelabel:off"
rssurl = 'https://news.yahoo.co.jp/pickup/rss.xml'


class Yahoo_API:

    def __init__(self):
        self.url = ""
        self.data = None

    def get_geocoder(self, query, return_type):
        self.url = geocoder_base.format(app_id=app_id, query=query, type=return_type)
        if return_type == "json":
            return self.json_get()["Feature"][0]["Geometry"]["BoundingBox"]
        else:
            return self.get()

    def get_precipitation(self, coordinates, return_type):
        self.url = weather_information_base.format(app_id=app_id, coordinates=coordinates, type=return_type)
        if return_type == "json":
            return self.json_get()
        else:
            return self.get()

    def json_get(self):
        return requests.get(url=self.url).json()

    def get(self):
        return requests.get(url=self.url)

    def get_rrd(self):
        return reader.format(app_id=app_id)

    def rss(self):
        return feedparser.parse(rssurl)

    def get_news(self) -> discord.Embed:
        rss = self.rss()
        embed = discord.Embed(title="Yahoo News", description="最新のニュースをおしらせします。")
        for entry in rss['entries']:
            r = requests.get(entry.link)
            soup = BeautifulSoup(r.text, 'lxml')
            data = soup.find("p", attrs={"class": "hbody"}).text
            embed.add_field(name=entry.title, value=data, inline=False)
        return embed
