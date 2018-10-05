from classes.baseworker import BaseWorker
from classes.decos import owner_only
import pickle
import re
import discord
from discord import Webhook, AsyncWebhookAdapter
import aiohttp
help_message = """
```
global-chat v2.0

名前がglobal-chatのチャンネルで発言をすると、自動でコネクトします。

commands:


commands(owner only):

!global del [id] delete message for id
```
"""


@owner_only
async def delete_message(author, delete_text: str, channels: list, client: discord.Client):
    channel = list(map(lambda x: client.get_channel(x), channels))
    for ch in channel:
        async for mess in ch.history():
            if mess.content == delete_text:
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
        super().__init__(client)
        try:
            with open('./apps/globalchat/data/global.pickle', mode='rb') as f:
                for key, value in pickle.load(f).items():
                    self.channels.append(value)
                    self.webhooks.append(key)
                    self.data[key] = value
        except FileNotFoundError:
            pass
        except EOFError:
            pass
        try:
            with open('./apps/globalchat/data/global-r18.pickle', mode='rb') as f:
                for key, value in pickle.load(f).items():
                    self.channels_r18.append(value)
                    self.webhooks_r18.append(key)
                    self.data_r18[key] = value
        except FileNotFoundError:
            pass
        except EOFError:
            pass

    async def join(self, message: discord.Message):
        await message.channel.send(help_message)
        return True

    async def on_message(self, message: discord.Message):
        if message.channel.id in self.channels:
            await self._send_webhook(message)
            return True
        if message.channel.id in self.channels_r18:
            await self._send_webhook(message, is_r18=True)
            return True
        if message.channel.name == "global-chat":
            await self._connect(message)
            return True
        if message.channel.name == "global-r18":
            await self._connect(message, is_r18=True)
            return True

    async def logout(self):
        with open('./apps/globalchat/data/global.pickle', mode='wb') as f:
            pickle.dump(self.data, f)
        with open('./apps/globalchat/data/global-r18.pickle', mode='wb') as f:
            pickle.dump(self.data_r18, f)

    async def command(self, message: discord.Message, command: str, args: list):
        if args[0] == "delete":
            delete_text = self.messages[int(args[1])]
            await delete_message(message.author, delete_text, self.channels, self.client)
            return True

    async def _connect(self, message: discord.Message, *, is_r18=False):
        if not is_r18:
            webhook = await message.channel.create_webhook(name="global-chat")
            self.channels.append(message.channel.id)
            self.webhooks.append(webhook.url)
            self.data[webhook.url] = message.channel.id
            # print(self.data)
            await message.channel.send(f"コネクトしました。コネクトチャンネル数:{len(self.channels)}")
            return True
        else:
            webhook = await message.channel.create_webhook(name="global-chat-r18")
            self.channels_r18.append(message.channel.id)
            self.webhooks_r18.append(webhook.url)
            self.data_r18[webhook.url] = message.channel.id
            # print(self.data_r18)
            await message.channel.send(f"コネクトしました。コネクトチャンネル数:{len(self.channels_r18)}")
            return True

    async def _send_webhook(self, message: discord.Message, *, is_r18=False):
        if not is_r18:
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
                for hook_url in self.webhooks:
                    if self.data[hook_url] == message.channel.id:
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
            self.messages[self.num] = message.content
            self.num += 1
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
            self.messages_r18[self.num_r18] = (message.embeds[0], message.author.id)
            self.num_r18 += 1
            return True


