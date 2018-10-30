import discord
from classes.baseworker import BaseWorker
import asyncio
help_message = """
```
Sigma timer v1.0.0

commands:

!timer [時間（分）] タイマーをセットします。
```
"""
timer = {}
timer_num = 0


async def background_task(time: int, uid: int, client: discord.Client, timer_id):
    await client.wait_until_ready()
    await asyncio.sleep(time * 60)
    author = client.get_user(uid)
    await author.send(f'{time}分のタイマーが終了しました。')
    del timer[timer_id]


class Worker(BaseWorker):
    async def join(self, message: discord.Message):
        # ここにかく
        await message.channel.send(help_message)
        return True

    async def command(self, message: discord.Message, command: str, args: list, point: int):
        global timer_num
        channel = message.channel
        if command == "!timer":
            if not args[0]:
                await channel.send("時間を指定してください！")
                return False
            try:
                num = int(args[0])
            except ValueError:
                await channel.send("数字で指定してください！")
                return False
            timer[timer_num] = {'time': num, 'id': message.author.id, 'def': num}
            await channel.send(f"{num}分のタイマーを開始しました。")
            self.client.loop.create_task(background_task(num, message.author.id, self.client, timer_num))
            timer_num += 1
            return True
