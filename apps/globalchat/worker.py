import aiofiles
import random
from classes.baseworker import BaseWorker
# from classes.decos import owner_only
import pickle
import re
import discord
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
from classes.math.Graph import pie_chart
import asyncio
help_message = """
```
global-chat v2.1.3

名前がglobal-chatのチャンネルで発言をすると、自動でコネクトします。

commands:

!global all -> 全てのコネクトしているサーバーを表示します。

!global sd -> 発言しているサーバーごとの発言数のグラフを表示します。

!global setnick [nick] -> グローバルチャットのニックネームを設定します。

!ad -> ADのメニューを表示します。

?g [message id(例:Ax6777)] [-del] 指定したメッセージの詳細を表示します。-delをつけると書いた本人かすみどらだけが消すことができます。

commands(owner only):

!global del [id] delete message for id

reference:

global-chatに送信するとき、 -from:[message id(例:Ax6777)] と指定すると、引用することができます。
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


def get_zero(tuple_list):
    for x in tuple_list:
        # print(tuple_list)
        yield x[0]


def create_key():
    one = random.choice("q,w,e,r,t,y,u,i,o,p,a,s,d,f,g,h,j,k,l,z,x,c,v,b,n,m".split(","))
    two = random.randint(0, 9)
    three = random.randint(0, 9)
    four = random.randint(0, 9)
    five = random.randint(0, 9)
    return "{0}x{1}{2}{3}{4}".format(one.upper(), two, three, four, five)


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
        self.ads = {}
        super().__init__(client)
        client.loop.create_task(self.load())
        client.loop.create_task(self.tips())
        client.loop.create_task(self.ad())

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
                self.ads = pickle.loads(await f.read())
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
            # print(self.messages)
            await self.send_webhook(message.guild, message.channel, message.author, message.content, message.attachments, message=message)
            return True
        if message.channel.id in self.channels_r18:
            await self.send_webhook(message.guild, message.channel, message.author, message.content, message.attachments, is_r18=True, message=message)
            return True
        if message.channel.name == "global-chat":
            await self._connect(message)
            return True
        if message.channel.name == "global-r18":
            await self._connect(message, is_r18=True)
            return True

    async def logout(self):
        for channel in self.channels:
            try:
                await self.client.get_channel(channel).send("sigma OS 終了します...")
            except:
                print(5)
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
                pickle.dump(self.ads, f)
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
            channel = message.channel
            mess = self.messages[args[0]]
            author = self.client.get_user(mess['author'])
            guild = self.client.get_guild(mess['guild'])
            if args[1] == "-del":
                if message.author.id == mess["author"] or message.author.id == 212513828641046529:
                    await channel.send(f"id:{args[0]}のメッセージを消去します...")
                    for x in mess['ids']:
                        try:
                            m = await self.client.get_channel(x[1]).get_message(x[0])
                            await m.delete()
                        except:
                            pass
                    await channel.send(f"id:{args[0]}のメッセージの消去に成功しました。")
                    del self.messages[args[0]]
                    return True
                else:
                    await channel.send(f"id:{args[0]}のメッセージの消去はメッセージの送信者かownerではないとできません。")
                    return -5
            embed = discord.Embed(title=f'{args[0]}のメッセージの詳細',
                                  description=f'author:{author.name}\n'
                                              f'guild:{guild.name}\n'
                                              f'author_id:{author.id}'
                                  )
            embed.add_field(name="content", value=mess['content'] if mess['content'] else "なし")
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
                if len(mess.content) > 200:
                    await channel.send("文章は200文字以内でお願いします。")
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
                if reaction.emoji == '🙅':
                    await m.channel.send("もう一度最初からやり直してください。")
                    return True
                await channel.send("全ての設定が完了しました！６回広告が表示されます！")
                self.ads[message.author.id] = {"content": mess.content.replace("@", "＠"), "count": 6}
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

    async def send_webhook(self, guild: discord.Guild, channel: discord.TextChannel, author: discord.Member, content: str, attachments: list, *, is_r18=False, is_ad=False, message=None, is_embed=False):
        if len(self.messages.keys()) > 150:
            self.messages.clear()
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
            quote = re.search("-from:([A-Z]x[0-9][0-9][0-9][0-9])", content)
            if quote:
                message_id = quote.groups()[0]
                mess = self.messages[message_id]
                _author = self.client.get_user(mess['author'])
                _guild = self.client.get_guild(mess['guild'])
                con = mess['content']
                embed = discord.Embed(description=con)
                embed.set_author(name=author.name, icon_url=_author.avatar_url)
                embed.set_footer(text=f"by {_guild.name} id:{message_id}")
                content = content.replace(f"-from:{message_id}", "")
            else:
                try:
                    if attachments:
                        embed = discord.Embed()
                        embed.set_image(url=attachments[0].url)
                    if is_embed:
                        embed.description = content
                except:
                    pass
            if len(content) > 250:
                await channel.send(f"{author.mention},250文字以上のメッセージは送信できません。")
                return False
            message_ids = []
            if message:
                message_ids.append((message.id, channel.id))
            key = create_key()
            async with aiohttp.ClientSession() as session:
                for hook_url in self.webhooks:
                    try:

                        if self.data[hook_url] == channel.id:
                            continue
                        webhook = Webhook.from_url(hook_url, adapter=AsyncWebhookAdapter(session))
                        webhook._adapter.store_user = webhook._adapter._store_user
                        webhook_message = await webhook.send(
                                           content,
                                           username=f'{username} at {key}',
                                           avatar_url=author.avatar_url,
                                           embed=embed if embed else None,
                                           wait=True
                        )
                        message_ids.append((webhook_message.id, self.data[hook_url]))
                        self.messages[key] = {
                            "ids": message_ids,
                            "embed": embed,
                            "message": message.id if message else None,
                            "channel": channel.id,
                            "guild": guild.id,
                            "author": author.id,
                            "content": content,
                            "reactions": "",
                            "reaction_users": {},
                            "reaction_messages": {},
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
            if message:
                message_ids.append(message.id)
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
                        message_ids.append((webhook_message.id, webhook_message.channel.id))
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
        delete_keys = []
        for key, value in self.speak_data.items():
            try:
                label.append(self.client.get_guild(key).name)
                data.append(value)
            except AttributeError:
                delete_keys.append(key)
        for x in delete_keys:
            del self.speak_data[x]
        pie_chart(data, label, "./datas/graph/speak_data.png")
        file = discord.File("./datas/graph/speak_data.png")
        await message.channel.send("global-chat 使用率のグラフです。", file=file)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        # print(reaction.message.channel.id)
        if reaction.message.channel.id in self.channels:
            for value in list(self.messages.items()):
                if reaction.message.id in list(get_zero(value[1]["ids"])):
                    if reaction.emoji in value[1]['reaction_users'].keys():
                        if user.id in value[1]['reaction_users'][reaction.emoji]:
                            return True
                    reaction_text = ''
                    if value[1]['reactions']:
                        reactions = value[1]['reactions'].split("\n")
                        already = False
                        for x in reactions:
                            data = x.split(":")
                            if data == ['']:
                                break
                            if data[0] == reaction.emoji:
                                already = True
                                reaction_text += f'{data[0]}: {int(data[1])+1}\n'
                                self.messages[value[0]]["reaction_users"][reaction.emoji].append(user.id)
                            else:
                                reaction_text += f'{data[0]}: {int(data[1])}\n'
                        if not already:
                            reaction_text += f'{reaction.emoji}: 1\n'
                            self.messages[value[0]]["reaction_users"][reaction.emoji] = [user.id]
                    else:
                        reaction_text += f'{reaction.emoji}: 1\n'
                        self.messages[value[0]]["reaction_users"] = {reaction.emoji: [user.id]}
                    self.messages[value[0]]['reactions'] = reaction_text
                    embed = discord.Embed(title=f"{value[0]}のメッセージにリアクションがつきました", description=reaction_text)
                    embed.add_field(name="content", value=value[1]["content"] if value[1]["content"] else "なし")
                    if value[1]['reaction_messages']:
                        for ids in self.channels:
                            try:
                                channel = self.client.get_channel(ids)
                                message = await channel.send(embed=embed)
                                channel_id = value[1]['reaction_messages'][channel.id]
                                delete_message = await channel.get_message(channel_id)
                                await delete_message.delete()
                                self.messages[value[0]]['reaction_messages'][channel.id] = message
                            except (AttributeError, discord.errors.Forbidden):
                                pass
                    else:
                        for ids in self.channels:
                            try:
                                channel = self.client.get_channel(ids)
                                message = await channel.send(embed=embed)
                                self.messages[value[0]]['reaction_messages'][channel.id] = message.id
                            except (AttributeError, discord.errors.Forbidden):
                                pass
                    return True

    async def ad(self):
        await self.client.wait_until_ready()
        await asyncio.sleep(10)
        guild = self.client.get_guild(499345248359809026)
        channel = self.client.get_channel(499345248359809028)
        while not self.client.is_closed():
            if self.ads:
                key = random.choice(list(self.ads.keys()))
                ad = self.ads[key]
                self.ads[key]["count"] -= 1
                if self.ads[key]["count"] == 0:
                    del self.ads[key]
                author = self.client.get_user(key)
                content = ad["content"]
                content = f"**--{author.name}さんのad--**\n{content}"
                await self.send_webhook(guild, channel, self.client.user, content, [], is_ad=True)
            await asyncio.sleep(1800)

    async def tips(self):
        await self.client.wait_until_ready()
        await asyncio.sleep(30)
        guild = self.client.get_guild(499345248359809026)
        channel = self.client.get_channel(499345248359809028)
        while not self.client.is_closed():
            content = "---tips---\n" + random.choice(tips)
            await self.send_webhook(guild, channel, self.client.user, content, [], is_ad=True)
            await asyncio.sleep(10800)
