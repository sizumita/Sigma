import discord
from classes.baseworker import BaseWorker
import aiofiles


class Worker(BaseWorker):
    def __init__(self, client: discord.Client):
        super().__init__(client)
        self.data = {}

    async def load(self):
        try:
            async with aiofiles.open('./datas/casino.pickle', 'rb') as f:
                data = await f.read()
        except (FileNotFoundError, EOFError):
            return
        for d in data.split("\n"):
            x = d.split(",")
            self.data[int(x[0])] = int(x[1])

    async def logout(self):
        if not self.data:
            return
        text = "\n".join([f"{key},{value}" for key, value in self.data.items()])
        async with aiofiles.open('./datas/casino.pickle', mode='wb') as stream:

            await stream.write(text)