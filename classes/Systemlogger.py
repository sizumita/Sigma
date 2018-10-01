import csv
import discord
import datetime
import pandas as pd
IMAGE_LOG_CHANNEL = 496103461532860416
COMMAND_LOG_CHANNEL = 495237526743678977


class logger:
    def __init__(self, client: discord.Client):
        self.command = "./logs/command.csv"
        self.ban = "./logs/ban.csv"
        self.client = client
        self.image_channel = client.get_channel(IMAGE_LOG_CHANNEL)
        self.command_channel = client.get_channel(COMMAND_LOG_CHANNEL)

    async def do_command(self, command, content, author_id, guild_id, channel_id, message: discord.Message):
        data = [command, content, author_id, guild_id, channel_id, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        self.write(data, self.command)
        embed = discord.Embed(title=f"{str(message.author)}がコマンドを使用しました！", description=f"コマンド:{command}")
        await self.command_channel.send(embed=embed)
        await self.command_channel.send(",".join(list(map(str, data))))

    def do_ban(self, *, banner_id, ban_user_id, reason):
        data = [banner_id, ban_user_id, reason, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        self.write(data, self.ban)

    async def send_image(self, message: discord.Message):
        atta = message.attachments
        for att in atta:
            await self.image_channel.send(att.url)

    def write(self, data: list, path: str):
        with open(path, 'a') as f:
            f.write("®".join(list(map(str, data))) + "\n")

    def read(self, path):
        df = pd.read_csv(path, sep="®", header=None)
        return df
