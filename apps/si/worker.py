import discord
import yaml
import asyncio
import pandas as pd
import csv
import os
import re
from classes.baseworker import BaseWorker
help_message = """
Server Settingsは、ただいま運用を停止しています。
"""
guilds = {}
all_guild = []
guild_paths = []
guild_names = {}


async def add_guild(guild: discord.Guild, channel: discord.TextChannel):
    path = "./apps/si/data/guilds/{.id}.yml".format(guild)
    if os.path.isfile(path):
        await channel.send("すでに登録されています！")
        return False

    data = {
        'name': guild.name,
        'channel': len(guild.channels),
        'created_at': guild.created_at,
        'icon': guild.icon_url,
        'owner_id': guild.owner_id,
        'evaluation': 0,
        'introduction': "",
    }
    with open(path, 'w') as f:
        f.write(yaml.dump(data))
    guilds[str(guild.id)] = data
    return True


class Worker(BaseWorker):
    def __init__(self, client: discord.Client):
        super().__init__(client)
        global guilds
        global all_guild
        global guild_paths
        self.client = client
        self.app_name = "si"
        all_guild = [re.match("^(.+).yml$", guild).groups()[0] for guild in
                     os.listdir('./apps/{app_name}/data/guilds'.format(app_name=self.app_name))
                     if guild.endswith(".yml")]
        guild_paths = ['./apps/{app_name}/data/guilds/'.format(app_name=self.app_name) + server for server in
                       os.listdir('./apps/{app_name}/data/guilds'.format(app_name=self.app_name))
                       if server.endswith(".yml")]
        for x in range(len(guild_paths)):
            path = guild_paths[x]
            with open(path, 'r') as f:
                data = yaml.load(f)
            guilds[all_guild[x]] = data

        for key in all_guild:
            guild = client.get_guild(int(key))
            guild_names[guild.name] = key

        print(guilds)

    async def loop(self, round_time: int, client: discord.Client):
        client = self.client

    async def on_message(self, message: discord.Message):
        pass
        # path = f'./apps/{self.app_name}/data/guilds/{message.guild.id}.csv'
        # async with open(path, 'a') as f:
        #     writer = csv.writer(f, lineterminator='\n')
        #     print('a')
        #     writer.writerow([message.created_at, str(message.author.id), str(message.channel.id), message.content])

    async def join(self, message: discord.Message):
        # ここにかく
        await message.channel.send(help_message)
        return True

    async def command(self, message: discord.Message, command: str, args: list):
        return self.join(message)
        # channel = message.channel
        # guild_id = str(message.guild.id)
        # if args[0] == "register":
        #     if not message.author.guild_permissions.administrator:
        #         await channel.send("Administer権限がありません！")
        #         return False
        #     if await add_guild(message.guild, message.channel):
        #         await channel.send("完了しました！次は、!si editで説明を書いて見ましょう！")
        #     return True
        # if args[0] == "info":
        #     if not guild_id in guilds.keys():
        #         await channel.send("このサーバーは登録されていません！\n!si registerで登録しましょう！")
        #         return False
        #     await message.channel.send("このサーバーの情報を表示します...")
        #     await asyncio.sleep(2)
        #     embed = discord.Embed(title=f"Guild:{message.guild.name}", description="このGuildの情報")
        #     embed.add_field(name="名前", value=guilds[guild_id]['name'], inline=False)
        #     embed.add_field(name="チャンネル数", value=guilds[guild_id]['channel'])
        #     embed.add_field(name="参加人数", value="{0}人 そのうちbot:{1} ユーザー:{2}人"
        #                     .format(len([u for u in message.guild.members]),
        #                             len([u for u in message.guild.members if u.bot]),
        #                             len([u for u in message.guild.members if not u.bot]),
        #                             ))
        #     embed.add_field(name="作成日", value=guilds[guild_id]["created_at"])
        #     embed.set_image(url=guilds[guild_id]["icon"])
        #     await channel.send(embed=embed)
        #     return True
