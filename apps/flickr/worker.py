from classes.baseworker import BaseWorker
from classes.FlickrAPI import flickr_get
import discord
help_message = """
```
Sigma Flickr Images v1.0.0

commands:

!fse [キーワード] ([画像枚数]) キーワードで検索した画像を表示します。
```
"""


class Worker(BaseWorker):
    async def join(self, message: discord.Message):
        # ここにかく
        await message.channel.send(help_message)
        return True

    async def command(self, message: discord.Message, command: str, args: list):
        channel = message.channel
        if command == "!fse":
            keyword = args[0]
            maisuu = 3
            if len(args) > 1:
                try:
                    maisuu = int(args[1]) + 1
                    if maisuu > 20:
                        await channel.send("枚数指定は20以内でおこなってください。")
                        return False
                except ValueError:
                    await channel.send("枚数指定は数字でおこなってください。")
                    return False
            res = flickr_get(keyword, maisuu)
            images = []
            for photo in res['photos']['photo']:
                try:
                    url_q = photo['url_q']
                except:
                    # print('url_qの取得に失敗しました')
                    continue
                images.append(url_q)
            for x in range(maisuu - 1):
                embed = discord.Embed(title=f"{keyword}の検索結果{x+1}", description="------")
                embed.set_image(url=images[x])
                await channel.send(embed=embed)