import discord
from classes.baseworker import BaseWorker
import aiofiles
import random
import asyncio
flag_choices = {
    "-h": lambda x, y: 1.5 if y > 30 else False,
    "-l": lambda x, y: 1.5 if y <= 30 else False,
    "multi": lambda x, y: 1.7 + 0.1 * x[1] if y % x[1] == 0 else False,
    "divis": lambda x, y: 2 if y % x[1] == 0 else False,
}
"""
Sigma Casino Test

commands:

.register ->仮登録します

.bal ->所持金を見ます

.dip ->Sigma pointをカジノコインに変換します。1point->10coin
"""


class Worker(BaseWorker):
    def __init__(self, client: discord.Client):
        super().__init__(client)
        self.data = {}
        client.loop.create_task(self.load())

    async def load(self):
        try:
            async with aiofiles.open('./datas/casino.txt', 'r') as f:
                data = await f.read()
        except (FileNotFoundError, EOFError):
            return
        for d in data.split("\n"):
            x = d.split(",")
            self.data[int(x[0])] = int(x[1])

    async def command(self, message: discord.Message, command: str, args: list, point: int):
        print(self.data)
        try:
            if command == ".dip":
                add_point = int(args[0])
                if not message.author.id in self.data.keys():
                    await message.channel.send("登録していません。`.register`")
                    return True
                if point < add_point:
                    await message.channel.send(f"Sigma Pointが不足しています。{point}<{add_point}")
                    return False
                self.data[message.author.id] += add_point * 10
                await message.channel.send(f"{add_point * 10}コインを振り込みました。")
                return -1 * add_point
            if command == ".register":
                if message.author.id in self.data.keys():
                    await message.channel.send("すでに登録済みです。")
                    return False
                await message.channel.send("ユーザーを登録しました。１万コイン配布されます...`.bal`")
                self.data[message.author.id] = 10000
                return True
            if command == ".bal":
                if not message.author.id in self.data.keys():
                    await message.channel.send("登録していません。`.register`")
                    return True
                coin = self.data[message.author.id]
                await message.channel.send(f"あなたの所持コインは、{coin}コインです。")
                return True
            if command == ".roul":
                price = int(args[0])
                # .roul [金額] [フラグ（掛ける場所、個数によって回す回数の指定）]
                if self.data[message.author.id] < price:
                    await message.channel.send(f"カジノコインが不足しています。")
                    return False
                self.data[message.author.id] -= price
                big_chance = False
                if random.choice([1, 1, 1, 1, 1, 1, 0]) == 0:
                    big_chance = True
                    await message.channel.send("BIG CHANCE!!!!!!獲得コイン数が５倍になります！")
                get_price = price
                del args[0]
                roul_num = 0
                await message.channel.send("ルーレット開始！")
                for f in args:
                    roul_num += 1
                    await message.channel.send("ルーレットを回します...")
                    await asyncio.sleep(2)
                    r = await self.roul(f)
                    if not r[0]:
                        await message.channel.send(f"{r[1]}が出た！\n外れてしまった...\nコインは一枚も返却されなかった...")
                        return False
                    if big_chance:
                        get_price *= 5
                    await message.channel.send(f"{r[1]}が出た！\nあたり！\n"
                                               f"連続{roul_num}回目！倍率{roul_num * 2}倍！{get_price * r[0] * roul_num * 2}"
                                               f"コインを入手した！")
                    get_price = get_price * r[0] * roul_num * 2
                self.data[message.author.id] += get_price
        except ValueError:
            await message.channel.send("金額指定は数字でおこなってください。")

    async def roul(self, flag: str):
        choice = random.randint(1, 60)
        f = flag.split(":")
        params = []
        for x in f:
            try:
                i = int(x)
            except ValueError:
                i = x
            params.append(i)
        print(params)

        if params[0] in flag_choices.keys():
            r = flag_choices[params[0]](params, choice)
            return r, choice
        else:
            return False, choice

    async def logout(self):
        if not self.data:
            return
        text = "\n".join([f"{key},{value}" for key, value in self.data.items()])
        async with aiofiles.open('./datas/casino.txt', mode='w') as stream:

            await stream.write(text)