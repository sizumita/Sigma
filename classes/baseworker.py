import discord


class BaseWorker:
    def __init__(self, client: discord.Client):
        self.client = client
        ...

    async def loop(self, round_time: int, client: discord.Client):
        ...

    async def on_message(self, message: discord.Message):
        ...

    async def join(self, message: discord.Message):
        ...

    async def command(self, message: discord.Message, command: str, args: list):
        return True

    async def logout(self):
        ...

    async def member_join(self, member: discord.Member):
        ...

    async def member_remove(self, member: discord.Member):
        ...
