from classes.baseworker import BaseWorker
import discord
from apps.bans import base_embed
import pandas as pd
import re
BAN_CHANNEL = 496140926087856138


class Worker(BaseWorker):
    def __init__(self, client: discord.Client):
        super().__init__(client)
        self.ch = client.get_channel(BAN_CHANNEL)

    async def join(self, message: discord.Message):
        await message.channel.send(embed=base_embed.help_embed)

    async def command(self, message: discord.Message, command: str, args: list):
        if command == ".gban":
            user = re.sub("[<@!>]", "", args[0])
            print(user)
            u = [i for i in self.client.get_all_members() if i.id == int(user)][0]
            del args[0]
            reason = " ".join(args)
            df = pd.DataFrame({"user": [str(u.id)], "reason": [reason], "guild": [str(message.guild.id)]})
            df.to_csv('./apps/bans/data/bans.csv', mode='a', header=False, sep='\t')
            await self.ch.send(f"user:{message.author.name}が{u.name}をBANしました。\n"
                               f"理由\n```\n{reason}\n```\nids:\nbanした人:{message.author.id}\n"
                               f"BANされた人:{u.id}")
            return True





