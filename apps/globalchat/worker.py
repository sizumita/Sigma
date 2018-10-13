import aiofiles
import random
from classes.baseworker import BaseWorker
from classes.decos import owner_only
import pickle
import re
import discord
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
from classes.math.Graph import pie_chart
import asyncio
help_message = """
```
global-chat v2.0

名前がglobal-chatのチャンネルで発言をすると、自動でコネクトします。

commands:

!global all -> 全てのコネクトしているサーバーを表示します。

!global sd -> 発言しているサーバーごとの発言数のグラフを表示します。

!global setnick [nick] -> グローバルチャットのニックネームを設定します。

commands(owner only):

!global del [id] delete message for id
```
"""
ad_help = """```
あなたのポイント:{}point

commands:

!ad new -> 新しい広告を作成します。作成に800コインが必要です。

!ad show -> 現在の広告を表示します。
```
"""
tips = [
    "`!global sd`で、global chatの使用率を確認することができます。",
    "`!fse`で、FlickrAPIで、画像を検索することができます。",
    "`!timer`で、タイマーを起動することができます。",
    "`!global all`で、全てのglobal chatにコネクトしているチャンネルを見ることができます。",
    "Sigmaの公式サーバーはこちら -> https://discord.gg/fVsAjm9"
]


def create_key():
    one = random.choice("q,w,e,r,t,y,u,i,o,p,a,s,d,f,g,h,j,k,l,z,x,c,v,b,n,m".split(","))
    two = random.randint(0, 9)
    three = random.randint(0, 9)
    four = random.randint(0, 9)
    five = random.randint(0, 9)
    return "{0}/{1}{2}{3}{4}".format(one, two, three, four, five)


@owner_only
async def delete_message(author, delete_text: str, delete_dict: str,  channels: list, client: discord.Client):
    channel = list(map(lambda x: client.get_channel(x), channels))
    for ch in channel:
        try:
            async for mess in ch.history():
                if mess.embeds:
                    if mess.embeds[0].to_dict() == delete_dict:
                        await mess.delete()
                else:
                    if delete_text in mess.content:
                        await mess.delete()
        except AttributeError:
            pass


class Worker(BaseWorker):
    def __init__(self, client: discord.Client):
        self.messages = {}
        self.num = 0
        self.channels = []
        self.webhooks = []
        self.data = {}
        self.messages_r18 = {}
        self.num_r18 = 0
        self.channels_r18 = []
        self.webhooks_r18 = []
        self.data_r18 = {}
        self.speak_data = {}
        self.nick = {}
        self.ad = {}
        super().__init__(client)
        client.loop.create_task(self.load())
        client.loop.create_task(self.tips())

    async def load(self):
        try:
            async with aiofiles.open('./datas/global.pickle', mode='rb') as f:
                for key, value in pickle.loads(await f.read()).items():
                    self.channels.append(value)
                    self.webhooks.append(key)
                    self.data[key] = value
        except (FileNotFoundError, EOFError):
            pass
        try:
            async with aiofiles.open('./datas/global-r18.pickle', mode='rb') as f:
                for key, value in pickle.loads(await f.read()).items():
                    self.channels_r18.append(value)
                    self.webhooks_r18.append(key)
                    self.data_r18[key] = value
        except (FileNotFoundError, EOFError):
            pass
        try:
            async with aiofiles.open('./datas/global_speak_data.pickle', mode='rb') as f:
                self.speak_data = pickle.loads(await f.read())
        except (FileNotFoundError, EOFError):
            pass
        try:
            async with aiofiles.open('./datas/global_nick.pickle', mode='rb') as f:
                self.nick = pickle.loads(await f.read())
        except (FileNotFoundError, EOFError):
            pass
        try:
            async with aiofiles.open('./datas/ad.pickle', mode='rb') as f:
                self.ad = pickle.loads(await f.read())
        except (FileNotFoundError, EOFError):
            pass
        for channel in self.channels:
            try:
                await self.client.get_channel(channel).send("sigma OS 起動します...")
            except (AttributeError, discord.errors.Forbidden):
                pass

    async def join(self, message: discord.Message):
        await message.channel.send(help_message)
        return True

    async def on_message(self, message: discord.Message):
        if message.channel.id in self.channels:
            await self.send_webhook(message.guild, message.channel, message.author, message.content, message.attachments)
            return True
        if message.channel.id in self.channels_r18:
            await self.send_webhook(message.guild, message.channel, message.author, message.content, message.attachments, is_r18=True)
            return True
        if message.channel.name == "global-chat":
            await self._connect(message)
            return True
        if message.channel.name == "global-r18":
            await self._connect(message, is_r18=True)
            return True

    async def logout(self):
        for channel in self.channels:
            await self.client.get_channel(channel).send("sigma OS 終了します...")
        try:
            with open('./datas/global.pickle', mode='wb') as f:
                pickle.dump(self.data, f)
            with open('./datas/global-r18.pickle', mode='wb') as f:
                pickle.dump(self.data_r18, f)
            with open('./datas/global_speak_data.pickle', mode='wb') as f:
                pickle.dump(self.speak_data, f)
            with open('./datas/global_nick.pickle', mode='wb') as f:
                pickle.dump(self.nick, f)
            with open('./datas/ad.pickle', mode='wb') as f:
                pickle.dump(self.ad, f)
        except:
            import traceback
            trace = traceback.format_exc()
            await self.client.get_channel(497046680806621184).send(trace)

    async def command(self, message: discord.Message, command: str, args: list, point: int):
        def pred(m):
            return m.author == message.author and m.channel == message.channel

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) in ['🆗', '🙅']
        if command == "!global":
            if args[0] == "delete":
                delete_text = self.messages[int(args[1])]['content']
                delete_dict = self.messages[int(args[1])]['embed']
                await message.channel.send(delete_text)
                await message.channel.send(delete_dict)
                await delete_message(message.author, delete_text, delete_dict, self.channels, self.client)
                return True
            if args[0] == "all":
                text = f"{len(self.channels)} channels\n"
                for x in self.channels:
                    channel = self.client.get_channel(x)
                    if not channel:
                        continue
                    text += f'global-chat on {channel.guild.name}\n'
                await message.channel.send(text)
                return True
            if args[0] == "sd":
                await self.show_speak_data(message)
                return True
            if args[0] == "setnick":
                del args[0]
                nick = " ".join(args)
                self.nick[message.author.id] = nick
                await message.channel.send(f"ニックネーム:{nick}　で保存されました。")

        elif command == "?g":
            try:
                num = int(args[0])
            except ValueError:
                await message.channel.send("そりゃ数字じゃねーぞ")
                return False
            mess = self.messages[num]
            author = self.client.get_user(mess['user_id'])
            guild = self.client.get_guild(mess['guild'])
            embed = discord.Embed(title=f'ナンバー{num}のメッセージの詳細', description=f'author:{author.name}\n'
                                                                           f'guild:{guild.name}\nauthor_id:{author.id}')
            embed.add_field(name="content", value=mess['content'])
            await message.channel.send(embed=embed)

        elif command == "!ad":
            if not args:
                await message.channel.send(ad_help.format(point))
                return True
            if args[0] == "new":
                channel = message.channel
                if point < 800:
                    await message.channel.send(f"あなたは必要なpointを持っていません！{point}<800")
                    return
                embed = discord.Embed(title="新しい広告を作成します...", description="広告の文章を入力してください..入力したら、"
                                                                          "\nここにプレビューが表示されます。")
                m = await message.channel.send(embed=embed)
                try:
                    mess = await self.client.wait_for('message', check=pred, timeout=30.0)
                except asyncio.TimeoutError:
                    await message.channel.send("👎")
                    return False
                if len(mess.content) > 100:
                    await channel.send("文章は100文字以内でお願いします。")
                    return -5
                embed.add_field(name="プレビュー", value=mess.content)
                embed.add_field(name="これで広告を作成しますか？", value="作成する場合は🆗、やり直す場合は🙅を押してください。")
                await m.edit(embed=embed)
                await m.add_reaction('🙅')
                await m.add_reaction('🆗')
                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                except asyncio.TimeoutError:
                    await m.channel.send('👎')
                    return False
                if reaction == '🙅':
                    await m.channel.send("もう一度最初からやり直してください。")
                    return True
                await channel.send("全ての設定が完了しました！６回広告が表示されます！")
                self.ad[message.author.id] = {"content": mess.content, "num": 6}
                return -800

    async def _connect(self, message: discord.Message, *, is_r18=False):
        webhook = None
        if await message.channel.webhooks():
            for x in await message.channel.webhooks():
                webhook = x
                break
        else:
            webhook = await message.channel.create_webhook(name="global-chat")
        if not is_r18:
            self.channels.append(message.channel.id)
            self.webhooks.append(webhook.url)
            self.data[webhook.url] = message.channel.id
            # print(self.data)
            await message.channel.send(f"コネクトしました。コネクトチャンネル数:{len(self.channels)}")
            self.speak_data[message.guild.id] = 0
            return True
        else:
            self.channels_r18.append(message.channel.id)
            self.webhooks_r18.append(webhook.url)
            self.data_r18[webhook.url] = message.channel.id
            # print(self.data_r18)
            await message.channel.send(f"コネクトしました。コネクトチャンネル数:{len(self.channels_r18)}")
            return True

    async def send_webhook(self, guild: discord.Guild, channel: discord.TextChannel, author: discord.Member, content: str, attachments: list, *, is_r18=False, is_ad=False):
        if author.id in self.nick:
            username = self.nick[author.id]
        else:
            username = author.name
        if not is_ad:
            if re.search("discord\.gg", content) or content.startswith("!"):
                return -1
        if not is_r18:
            content = content.replace("@", "＠")
            embed = None
            try:
                if attachments:
                    embed = discord.Embed()
                    embed.set_image(url=attachments[0].url)
            except:
                pass
            if len(content) > 250:
                await channel.send(f"{author.mention},250文字以上のメッセージは送信できません。")
                return False
            # embed.set_author(name=str(author), icon_url=author.avatar_url)
            # embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            # embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            message_ids = []
            async with aiohttp.ClientSession() as session:
                for hook_url in self.webhooks:
                    try:
                        if self.data[hook_url] == channel.id:
                            continue
                        webhook = Webhook.from_url(hook_url, adapter=AsyncWebhookAdapter(session))
                        webhook._adapter.store_user = webhook._adapter._store_user
                        webhook_message = await webhook.send(
                                           content,
                                           username=f'{username} id:{self.num}',
                                           avatar_url=author.avatar_url,
                                           embed=embed if embed else None,
                                           wait=True
                        )
                        message_ids.append(webhook_message.id)
                        self.messages[self.num] = {
                            "ids": message_ids,
                            "embed": embed
                        }
                    except discord.errors.NotFound:
                        pass
            if not guild.id in self.speak_data.keys():
                self.speak_data[guild.id] = 1
                return True
            self.speak_data[guild.id] += 1
            return True
        else:
            content = content.replace("@", "＠")
            embed = discord.Embed(description=content)
            try:
                if attachments:
                    embed.set_image(url=attachments[0].url)
            except:
                pass
            if len(content) > 250:
                await channel.send(f"{author.mention},250文字以上のメッセージは送信できません。")
                return False
            embed.set_author(name=str(author), icon_url=author.avatar_url)
            embed.set_footer(text=guild.name, icon_url=guild.icon_url)
            # embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            message_ids = []
            async with aiohttp.ClientSession() as session:
                for hook_url in self.webhooks:
                    try:
                        if self.data[hook_url] == channel.id:
                            continue
                        webhook = Webhook.from_url(hook_url, adapter=AsyncWebhookAdapter(session))
                        webhook._adapter.store_user = webhook._adapter._store_user
                        webhook_message = await webhook.send(
                            content,
                            username=f'{username} id:{self.num}',
                            avatar_url=author.avatar_url,
                            embed=embed,
                            wait=True
                        )
                        message_ids.append(webhook_message.id)
                        self.messages[self.num] = {
                            "ids": message_ids,
                        }
                    except discord.errors.NotFound:
                        pass
            if not guild.id in self.speak_data.keys():
                self.speak_data[guild.id] = 1
                return True
            self.speak_data[guild.id] += 1
            return True

    async def show_speak_data(self, message: discord.Message):
        data = []
        label = []
        for key, value in self.speak_data.items():
            try:
                label.append(self.client.get_guild(key).name)
                data.append(value)
            except AttributeError:
                del self.speak_data[key]
        pie_chart(data, label, "./datas/graph/speak_data.png")
        file = discord.File("./datas/graph/speak_data.png")
        await message.channel.send("global-chat 使用率のグラフです。", file=file)

    async def ad(self):
        guild = self.client.get_guild(499345248359809026)
        channel = self.client.get_channel(499345248359809028)
        content = ""
        while not self.client.is_closed():
            pass
        await self.send_webhook(guild, channel, self.client.user, content, [], is_ad=True)

    async def tips(self):
        await self.client.wait_until_ready()
        await asyncio.sleep(30)
        guild = self.client.get_guild(499345248359809026)
        channel = self.client.get_channel(499345248359809028)
        while not self.client.is_closed():
            content = "---tips---\n" + random.choice(tips)
            await self.send_webhook(guild, channel, self.client.user, content, [], is_ad=True)
            await asyncio.sleep(10800)
