from classes.baseworker import BaseWorker
import discord
from apps.bans import base_embed
import pandas as pd
import re
import asyncio
import pickle
owners = [293654928331898880, 212513828641046529]
BAN_CHANNEL = 496140926087856138


class Worker(BaseWorker):
    def __init__(self, client: discord.Client):
        super().__init__(client)
        self.ch = client.get_channel(BAN_CHANNEL)
        self.guilds = {}
        try:
            with open('./apps/bans/data/settings.pickle', 'rb') as f:
                self.guilds = pickle.load(f)
        except (FileNotFoundError, EOFError):
            pass

    async def join(self, message: discord.Message):
        await message.channel.send(embed=base_embed.help_embed)

    async def command(self, message: discord.Message, command: str, args: list):
        def check(m):
            return m.author == message.author and m.channel == message.channel
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
            await message.channel.send(f"user:{message.author.name}が{u.name}をBANしました。\n"
                                       f"理由\n```\n{reason}\n```\nids:\nbanした人:{message.author.id}\n"
                                       f"BANされた人:{u.id}")
            await message.author.ban(reason=reason)
            return True
        if command == ".protect":
            pex = message.author.guild_permissions
            for x in pex:
                if x == ('administrator', True):
                    break
                elif x == ('administrator', False):
                    await message.channel.send("error: あなたには必要な権限がありません！\n必要な権限: Administer")
            if args[0] == "start":
                if message.guild.id in self.guilds:
                    await message.channel.send("error: すでに登録されています。")
                    return True
                self.guilds[message.guild.id] = []
                await message.channel.send("登録しました。")
                return True
            if args[0] == "set":
                uid = re.sub("[<@!?&>]", "", args[1])
                if message.guild.id in self.guilds.keys():
                    self.guilds[message.guild.id].append(uid)
                    await message.channel.send("設定しました。")
                    return True
                await message.channel.send("error: 登録されていません。")
                return True
            if args[0] == "stop":
                if message.guild.id in self.guilds:
                    del self.guilds[message.guild.id]
                    await message.channel.send("解除しました。")
                    return True
                await message.channel.send("error: 登録されていません。")
                return True
            return True
        if command == ".unban":
            if not message.author.id in owners:
                await message.channel.send("あなたにはその権限がありません！")
                return False
            mes = None
            df = pd.read_table('./apps/bans/data/bans.csv', header=None)
            await message.channel.send("消したいbanを選択してください！")
            await message.channel.send(df)
            bans = df.values.tolist()
            try:
                mes = await self.client.wait_for("message", check=check, timeout=30)
            except asyncio.TimeoutError:
                await message.channel.send('\N{THUMBS DOWN SIGN}')
            for b in bans:
                if int(mes.content) == b[0]:
                    df.drop(int(mes.content))
                    # df = df.reset_index(drop=True)
                    del df[0]
                    df.to_csv('./apps/bans/data/bans.csv', header=False, sep='\t')
                    u = self.client.get_user(b[1])
                    guild = self.client.get_guild(b[3])
                    reason = b[2]
                    embed = discord.Embed(title=f"{u.name}のbanを解除しました。", description=f"GUild:{guild.name}")
                    embed.add_field(name="理由", value=reason)
                    embed.add_field(name="invite", value=str(await guild.text_channels[0].create_invite()))
                    embed.set_image(url=guild.icon_url)
                    await message.channel.send(embed=embed)

    async def on_message(self, message: discord.Message):
        content = message.clean_content
        if "@everyone" in content or re.search("discord(\.gg|app\.com)/.*", content):
            pex = message.author.guild_permissions
            for x in pex:
                if x == ('manage_messages', True):
                    return True
            if message.guild.id in self.guilds:
                role_ids = [x.id for x in message.author.roles]
                for x in role_ids:
                    if x in self.guilds:
                        return True
                await message.delete()
                await message.channel.send("```cpp\n# everyoneメンションか招待を許可がないユーザーが送信しました。\nkickします。\n```")
                await message.author.send("```cpp\n# あなたはeveryoneメンションか招待を許可がない状態で投稿したので、キックされました。\n```")
                await message.author.kick()
            return True

    async def logout(self):
        try:
            with open('./apps/bans/data/settings.pickle', 'wb') as f:
                pickle.dump(self.guilds, f)
        except (FileNotFoundError, EOFError):
            pass
