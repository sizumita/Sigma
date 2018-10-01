import discord

from apps.pyhelp.text import get_help
from classes.baseworker import BaseWorker


class Worker(BaseWorker):
    async def command(self, message: discord.Message, command: str, args: list):
        if command == "?py":
            text = args[0]
            del args[0]
            flags = args
            data = get_help(text, flags)
            print(data)
            if type(data) == discord.Embed:
                await message.channel.send(embed=data, delete_after=20.0)
            else:
                await message.channel.send(data, delete_after=20.0)
