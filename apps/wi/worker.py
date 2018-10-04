import asyncio
import discord
from classes.yahoo_api import Yahoo_API
from classes.OpenWeatherMap import get_weather_forecast, get_weather
from classes.baseworker import BaseWorker
import requests
import datetime
help_message = """
```
Weather Information

コマンド一覧

!wi help -> これを表示します。

!wi pp -> 入力した地点の今の降水量とこれからの降水量の予想を表示します。

!wi weather -> 入力した地点の天気予報を表示します。

!wi weather_yahoo -> 入力した地点の天気予報を表示します。(yahoo、バグがありマス。)
あ
!wi mscale -> Mスケールを取得できます。

!wi taifu -> 最新の台風情報がゲットできます。

!wi rrd -> 最新の雨雲レーダーが表示されます。
```
"""


class Worker(BaseWorker):

    async def join(self, message: discord.Message):
        # ここにかく
        await message.channel.send(help_message)
        return True

    async def command(self, message: discord.Message, command: str, args: list):
        def pred(m):
            return m.author == message.author and m.channel == message.channel
        client = self.client
        if args[0] == "pp":
            await message.channel.send("市や県の名前や地名を入力してください。")
            try:
                ll = await client.wait_for('message', check=pred, timeout=30)
            except asyncio.TimeoutError:
                return False
            api = Yahoo_API()
            data = api.get_geocoder(ll.content, "json")
            ll_data = data.split(" ")
            weather = api.get_precipitation(ll_data[0], "json")["Feature"][0]["Property"]["WeatherList"]["Weather"]
            embed = discord.Embed(title="{}のこれからの降水確率".format(ll.content), description="これから６０分の降水量（予測）を表示します")
            for x in range(7):
                embed.add_field(name="{}0分後".format(x), value=str(weather[x]["Rainfall"]) + "mm/h")
            await message.channel.send(embed=embed)
            return True
        if args[0] == "weather_yahoo":
            await message.channel.send("市や県の名前や地名を入力してください。")
            try:
                ll = await client.wait_for('message', check=pred, timeout=30)
            except asyncio.TimeoutError:
                return False
            api = Yahoo_API()
            data = api.get_geocoder(ll.content, "json")
            ll_data = data.split(" ")[0]
            base_ll_data = ll_data.split(",")
            weather_data = get_weather_forecast(base_ll_data[1], base_ll_data[0])
            embed = discord.Embed(title="{.content}のこれからの天気".format(ll), description="3時間ごとの天気を表示します")
            num = 0
            time = 0
            for sort_key in weather_data[1]:
                value = weather_data[0][sort_key]
                embed.add_field(name="{}時間後の天気".format(time), value=value, inline=False)
                num += 1
                time += 3
                if num == 10:
                    break
            await message.channel.send(embed=embed)
            return True
        if args[0] == "weather":
            await message.channel.send("市や県の名前を入力してください。")
            try:
                ll = await client.wait_for('message', check=pred, timeout=30)
            except asyncio.TimeoutError:
                return False
            data = get_weather(ll.content)
            if data['cod'] == '404':
                await message.channel.send("都市名が不明です。県や市などの言葉を削除し、地名も削除してください。\n"
                                           "また、ローマ字の地名にすることをお勧めします。例: 大阪 -> Osaka")
                return True
            weather = data['weather'][0]
            temp = data['main']
            wind = data['wind']
            embed = discord.Embed(title=f'{ll.content}の天気', description="------")
            embed.add_field(name="天気", value=weather['main'])
            embed.add_field(name="気温", value=str(temp['temp']) + "℃")
            embed.add_field(name="最低気温", value=str(temp['temp_min']) + "℃")
            embed.add_field(name="最高気温", value=str(temp['temp_max']) + "℃")
            embed.add_field(name="風速", value=str(wind['speed']) + "m/s")
            await message.channel.send(embed=embed)
            # await message.channel.send(data)
        if args[0] == "mscale":
            req = requests.get("http://weathernews.jp/mscale/mscale_json.cgi")
            await message.channel.send("今のMスケールは{}です。".format(req.json()['mscale'][1]))
            return True
        if args[0] == "taifu":
            req = requests.get("http://weathernews.jp/s/typhoon/cgi/typhoon_json.fcgi")
            data = req.json()
            if not data:
                await message.channel.send("台風情報はありません。")
                return True
            json_data = data[0]
            name = json_data["name"]  # 台風の名称
            comment_title = json_data["comment_title"]  # 台風chのトピック
            comment_body = json_data["comment_body"]  # 本文
            analized_date = json_data["analized_date"]  # 更新時刻
            date = json_data["details"][0]["date"]  # 現在情報
            location = json_data["details"][0]["location"]  # 現在位置
            latitude = json_data["details"][0]["latitude"]  # 現在位置 緯度
            longitude = json_data["details"][0]["longitude"]  # 現在位置 経度
            size = json_data["details"][0]["size"]  # 台風の大きさ
            strength = json_data["details"][0]["strength"]  # 台風の勢力
            direction = json_data["details"][0]["direction"]  # 台風の方向・速さ
            pressure = json_data["details"][0]["pressure"]  # 台風の中心気圧
            maxwind = json_data["details"][0]["maxwind"]  # 最大風速
            windgust = json_data["details"][0]["windgust"]  # 最大瞬間風速
            embed = discord.Embed(title="台風情報", color=0xeee657)
            embed.add_field(name="台風の名称", value=name, inline=False)
            embed.add_field(name="現在位置", value=location, inline=False)
            embed.add_field(name="座標", value=latitude + longitude)
            embed.add_field(name="大きさ", value=size)
            embed.add_field(name="勢力", value=strength)
            embed.add_field(name="方向・速さ", value=direction, inline=False)
            embed.add_field(name="中心気圧", value=pressure, inline=False)
            embed.add_field(name="最大風速", value=maxwind, inline=False)
            embed.add_field(name="最大瞬間風速", value=windgust, inline=False)
            embed.add_field(name=comment_title, value=comment_body)
            embed.add_field(name="更新", value=analized_date)
            embed.set_image(url="http://weathernews.jp" + json_data['img'])
            await message.channel.send(embed=embed)
            return True
        if args[0] == "rrd":
            api = Yahoo_API()
            url = api.get_rrd()
            embed = discord.Embed(title="雨雲レーダー", description="現在の雨雲の様子です")
            embed.set_image(url=url)
            await message.channel.send(embed=embed)
            return True




