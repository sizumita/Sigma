import asyncio
import os
import random
import discord
from classes import User
from classes import AppManager
from classes.Systemlogger import logger
from os.path import join, dirname
from dotenv import load_dotenv

useing = []
owners = ["212513828641046529"]
users = {}
sessions = {}
add_point_user = []
app_path = "./apps/"


class MyClient(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.logger = None
        self.app_manager = None

    async def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print(client.is_closed())
        print('------')
        await client.change_presence(activity=discord.Game(name='すみどらちゃん: sigma'))
        self.app_manager = AppManager.AppManager(client)
        self.logger = logger(self)
        await self.app_manager.set_up()

    async def on_message(self, message: discord.Message):
        try:
            if message.attachments and not message.author.bot:
                await self.logger.send_image(message)
        except:
            pass
        try:
            if await check(message):
                return
            useing.append(message.author.id)
            if message.content == "sigma stop" and message.author.id == 212513828641046529:
                await self.app_manager.logout()
            # アプリコマンド
            data = await self.app_manager.catch_command(message)
            if not data == [False, False]:
                app, command = data[0], data[1]
                await self.logger.do_command(command=command, content=message.content,
                                             author_id=message.author.id, guild_id=message.guild.id,
                                             channel_id=message.channel.id, message=message)
                if app:
                    useing.remove(message.author.id)
                    if not type(app) == bool:
                        if type(app) == int:
                            user = get_user(message.author.id)
                            user.add_point(app)
                    return True

            if message.content.startswith("sigma"):
                if not str(message.author.id) in users.keys():
                    await self.sigma_start(message)
                app = await self.load_os(message)
                await self.logger.do_command(command="sigma", content=message.content,
                                             author_id=message.author.id, guild_id=message.guild.id,
                                             channel_id=message.channel.id, message=message)
                if type(app) != bool:
                    if type(app) == int:
                        user = get_user(message.author.id)
                        user.add_point(app)
                    if type(app) == str:
                        if app == "apps":
                            await self.app_manager.show_apps(message)
                await self.app_manager.start(message)

            if message.author.id == "212513828641046529":
                if message.content.startswith("sigma app reload"):
                    await self.app_manager.set_up()

            useing.remove(message.author.id)

        except:
            import traceback
            trace = traceback.format_exc()
            await message.channel.send(trace)
            useing.remove(message.author.id)

        else:
            if await check(message):
                return
            if not str(message.author.id) in users.keys():
                await self.app_manager.message_on(message)
                return
            if not message.author.id in add_point_user \
                    and not message.content.startswith("sigma "):
                try:
                    user = get_user(message.author.id)
                    if isinstance(user, bool):
                        return
                    user.add_point(random.randint(5, 15))
                    add_point_user.append(message.author.id)
                    await asyncio.sleep(60)
                    add_point_user.remove(message.author.id)
                except:
                    pass

    async def on_member_join(self, member: discord.Member):
        print(1)
        await self.app_manager.member_join(member)

    async def send(self, to: discord.TextChannel, message):
        await to.send(f"```\n{message}\n```")

    async def sigma_start(self, message: discord.Message):
        h = self.get_channel(496450097928732672)
        users[str(message.author.id)] = User.User(message.author.id, client)
        await message.channel.send(str(await h.create_invite()))
        await self.send(message.channel, f"ユーザーデータのロード完了。\nこんにちは、{message.author.name}さん。")

    async def load_os(self, message: discord.Message):
        return await self.app_manager.command(message, 'sigma', 'os')


async def check(message: discord.Message):
    if message.author.bot:
        return True
    if message.author.id == client.user.id:
        return True
    if message.author.id in useing:
        return True

    return False


def get_user(uid: int) -> User:
    if str(uid) in users.keys():
        return users[str(uid)]
    return False


def shutdown():
    client.loop.stop()


client = MyClient()

dotenv_path = join(dirname(__file__), '../sigma.env')
load_dotenv(dotenv_path)
try:
    client.run(os.environ.get("TOKEN"))

except:
    shutdown()
