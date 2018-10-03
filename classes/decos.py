import discord
from classes.baseworker import BaseWorker


def owner_only(func):
    async def wrapper(*args, **kwargs):
        if isinstance(args[0], discord.Message):
            author = args[0].author
        elif isinstance(args[0], discord.Member):
            author = args[0]
        elif isinstance(args[0], BaseWorker):
            author = args[1].author
        else:
            return
        if author.id == 212513828641046529:
            await func(*args, **kwargs)
        else:
            await author.send("実行できません。")
    return wrapper
