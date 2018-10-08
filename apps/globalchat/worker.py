import aiofiles

from classes.baseworker import BaseWorker
from classes.decos import owner_only
import pickle
import re
import discord
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
from classes.math.Graph import pie_chart
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


@owner_only
async def delete_message(author, delete_text: str, delete_dict: str,  channels: list, client: discord.Client):
    channel = list(map(lambda x: client.get_channel(x), channels))
    for ch in channel:
        async for mess in ch.history():
            if mess.embeds:
                if mess.embeds[0].to_dict() == delete_dict:
                    await mess.delete()
            else:
                if delete_text in mess.content:
                    await mess.delete()


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
        super().__init__(client)
        client.loop.create_task(self.load())

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

    async def join(self, message: discord.Message):
        await message.channel.send(help_message)
        return True

    async def on_message(self, message: discord.Message):
        if message.channel.id in self.channels:
            await self.send_webhook(message)
            return True
        if message.channel.id in self.channels_r18:
            await self.send_webhook(message, is_r18=True)
            return True
        if message.channel.name == "global-chat":
            await self._connect(message)
            return True
        if message.channel.name == "global-r18":
            await self._connect(message, is_r18=True)
            return True

    async def logout(self):
        with open('./datas/global.pickle', mode='wb') as f:
            pickle.dump(self.data, f)
        with open('./datas/global-r18.pickle', mode='wb') as f:
            pickle.dump(self.data_r18, f)
        with open('./datas/global_speak_data.pickle', mode='wb') as f:
            pickle.dump(self.speak_data, f)

    async def command(self, message: discord.Message, command: str, args: list):
        if command == "!global":
            if args[0] == "delete":
                delete_text = self.messages[int(args[1])]['content']
                delete_dict = self.messages[int(args[1])]['embed']
                await delete_message(message.author, delete_text, delete_dict, self.channels, self.client)
                return True
            if args[0] == "auto_connect":
                await self.auto_connect(message)
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
            print(args)
            try:
                num = int(args[0])
            except ValueError:
                await message.channel.send("そりゃ数字じゃねーぞ")
                return False
            mess = self.messages[int(args[1])]
            author = self.client.get_user(mess['user_id'])
            guild = self.client.get_guild(mess['guild'])
            embed = discord.Embed(title=f'ナンバー{num}のメッセージの詳細', description=f'author:{author.name}\n'
                                                                           f'guild:{guild.name}\nauthor_id:{author.id}')
            embed.add_field(name="content", value=mess['content'])

    async def _connect(self, message: discord.Message, *, is_r18=False):
        if not is_r18:
            webhook = await message.channel.create_webhook(name="global-chat")
            self.channels.append(message.channel.id)
            self.webhooks.append(webhook.url)
            self.data[webhook.url] = message.channel.id
            # print(self.data)
            await message.channel.send(f"コネクトしました。コネクトチャンネル数:{len(self.channels)}")
            self.speak_data[message.guild.id] = 0
            return True
        else:
            webhook = await message.channel.create_webhook(name="global-chat-r18")
            self.channels_r18.append(message.channel.id)
            self.webhooks_r18.append(webhook.url)
            self.data_r18[webhook.url] = message.channel.id
            # print(self.data_r18)
            await message.channel.send(f"コネクトしました。コネクトチャンネル数:{len(self.channels_r18)}")
            return True

    async def send_webhook(self, message: discord.Message, *, is_r18=False):
        if message.author.id in self.nick:
            username = self.nick[message.author.id]
        else:
            username = message.author.name
        if not is_r18:
            content = message.content.replace("@", "＠")
            if re.search("discord\.gg", content) or content.startswith("!"):
                return -1
            embed = discord.Embed(title=content)
            try:
                if message.attachments:
                    embed.set_image(url=message.attachments[0].url)
            except:
                pass
            embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
            embed.set_footer(text=message.guild.name, icon_url=message.guild.icon_url)
            # embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
            async with aiohttp.ClientSession() as session:
                for hook_url in self.webhooks:
                    try:
                        if self.data[hook_url] == message.channel.id:
                            continue
                        webhook = Webhook.from_url(hook_url, adapter=AsyncWebhookAdapter(session))
                        await webhook.send(
                                           # content + f'\nuserid:{message.author.id}',
                                           username=f'{username} id:{self.num}',
                                           avatar_url=message.author.avatar_url,
                                           embed=embed)
                    except discord.errors.NotFound:
                        pass
            self.messages[self.num] = {
                                       "content": message.content,
                                       "embed": embed.to_dict(),
                                       "user_id": message.author.id,
                                       "guild": message.guild.id,
                                       }
            self.num += 1
            if not message.guild.id in self.speak_data.keys():
                self.speak_data[message.guild.id] = 1
                return True
            self.speak_data[message.guild.id] += 1
            return True
        else:
            content = message.content.replace("@", "＠")
            if re.search("discord\.gg", content) or content.startswith("!"):
                return -1
            embed = None
            try:
                if message.attachments:
                    embed = discord.Embed()
                    embed.set_image(url=message.attachments[0].url)
            except:
                pass
            async with aiohttp.ClientSession() as session:
                for hook_url in self.webhooks_r18:
                    if self.data_r18[hook_url] == message.channel.id:
                        continue
                    webhook = Webhook.from_url(hook_url, adapter=AsyncWebhookAdapter(session))
                    if embed:
                        await webhook.send(content + f'\nuserid:{message.author.id}',
                                           username=f'{message.author.name} id:{self.num}',
                                           avatar_url=message.author.avatar_url,
                                           embed=embed)
                    else:
                        await webhook.send(content + f'\nuserid:{message.author.id}',
                                           username=f'{message.author.name} id:{self.num}',
                                           avatar_url=message.author.avatar_url)
            self.messages_r18[self.num_r18] = {"content": message.content,
                                               "embed": embed.to_dict(),
                                               "user_id": message.author.id,
                                               "guild": message.guild.id,
                                               }
            self.num_r18 += 1
            return True

    @owner_only
    async def auto_connect(self, message: discord.Message):
        for guild in self.client.guilds:
            for channel in guild.channels:
                print(channel.name)
                try:
                    if channel.name == "global-chat":
                        if message.channel.id in self.channels:
                            continue
                        if await channel.webhooks():
                            self.channels.append(channel.id)
                            self.webhooks.append(await channel.webhooks()[0].url)
                            self.data[await channel.webhooks()[0].url] = channel.id
                            await channel.send(f"コネクトしました。コネクトチャンネル数:{len(self.channels)}")
                            continue
                        webhook = await channel.create_webhook(name="global-chat")
                        self.channels.append(channel.id)
                        self.webhooks.append(webhook.url)
                        self.data[webhook.url] = channel.id
                        await channel.send(f"コネクトしました。コネクトチャンネル数:{len(self.channels)}")
                        return True
                    if channel.name == "global-r18":
                        if message.channel.id in self.channels_r18:
                            continue
                        if await channel.webhooks():
                            self.channels_r18.append(channel.id)
                            self.webhooks_r18.append(await channel.webhooks()[0].url)
                            self.data_r18[await channel.webhooks()[0].url] = channel.id
                            await channel.send(f"コネクトしました。コネクトチャンネル数:{len(self.channels_r18)}")
                            continue
                        webhook = await channel.create_webhook(name="global-chat")
                        self.channels_r18.append(channel.id)
                        self.webhooks_r18.append(webhook.url)
                        self.data_r18[webhook.url] = channel.id
                        await channel.send(f"コネクトしました。コネクトチャンネル数:{len(self.channels_r18)}")
                        return True
                except:
                    pass

    async def show_speak_data(self, message: discord.Message):
        data = []
        label = []
        for key, value in self.speak_data:
            data.append(value)
            label.append(key)
        pie_chart(data, label, "./datas/graph/speak_data.png")
        file = discord.File("./datas/graph/speak_data.png")
        await message.channel.send("global-chat 使用率のグラフです。", file=file)
