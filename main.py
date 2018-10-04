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
system_ban_id = []
try:
    with open('./logs/system_ban.txt', 'w') as f:
        text = f.read()
        for x in text.split(','):
            system_ban_id.append(int(x))
except:
    pass


class MyClient(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.logger = None
        self.app_manager = None
        self.error = None
        self.delete_check = []

    async def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print(client.is_closed())
        print('------')
        await client.change_presence(activity=discord.Game(name='すみどらちゃん: sigma'))
        self.app_manager = AppManager.AppManager(client)
        self.logger = logger(self)
        self.error = self.get_channel(497046680806621184)
        await self.app_manager.set_up()

    async def on_message(self, message: discord.Message):
        global system_ban_id, users, sessions, useing, add_point_user
        try:
            if message.attachments and not message.author.bot:
                await self.logger.send_image(message)
            # elif "discord.gg" in message.content:
                # await self.logger.send_invite(message)
        except:
            pass
        if message.content == "sigma rc" and message.author.id == 212513828641046529:
            await self.rc(message)
            return
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
                        elif type(app) == str:
                            if app.startswith("ban "):
                                user_id = app.split()[1]
                                system_ban_id.append(int(user_id))
                            elif app.startswith("unban "):
                                user_id = app.split()[1]
                                system_ban_id.remove(int(user_id))
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
            await self.error.send(trace)
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
        await self.app_manager.member_join(member)

    # async def on_member_remove(self, member: discord.Member):
    #     await self.app_manager
    async def on_message_delete(self, message: discord.Message):
        if message.channel.id in self.delete_check:
            if message.author.id == self.user.id:
                await message.channel.send(message.content)
                return
            text = f"""
            消されたメッセージ
            ```
            {message.author.name} {message.created_at}
            {message.content}
            ```
            """
            await message.channel.send(text)

    async def send(self, to: discord.TextChannel, message):
        await to.send(f"```\n{message}\n```")

    async def sigma_start(self, message: discord.Message):
        # h = self.get_channel(496450097928732672)
        users[str(message.author.id)] = User.User(message.author.id, client)
        # await message.channel.send(str(await h.create_invite()))

        await self.send(message.channel, f"ユーザーデータのロード完了。\nこんにちは、{message.author.name}さん。")

    async def load_os(self, message: discord.Message):
        return await self.app_manager.command(message, 'sigma', 'os')

    async def rc(self, message: discord.Message):
        channel = message.channel
        await channel.send("Sigma リカバリーモード　起動\n"
                           "何をしますか？番号を選んでください。\n"
                           "1:チャンネルチェック -> 消されたメッセージを再度送信します。\n"
                           "2:今のpermissionを送ります。")

        def pred(m):
            return m.author == message.author and m.channel == message.channel
        try:
            mess = await self.wait_for('message', check=pred, timeout=30)
        except asyncio.TimeoutError:
            return False
        if mess.content == "1":
            self.delete_check.append(channel.id)
            await channel.send("追加")
            return
        if mess.content == "2":
            t = "\n".join([i[0] + ":" + str(i[1]) for i in message.guild.me.guild_permissions])
            await message.author.send(t)
            return


async def check(message: discord.Message):
    try:
        if not message.guild.me.guild_permissions.administrator:
            return True
    except:
        pass
    if message.author.id in system_ban_id:
        return True
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
    with open('./logs/system_ban.txt', 'w') as f:
        text = ",".join([str(i) for i in system_ban_id])
        f.write(text)
    client.loop.stop()


client = MyClient()

dotenv_path = join(dirname(__file__), '../sigma.env')
load_dotenv(dotenv_path)
try:
    client.run(os.environ.get("TOKEN"))

except:
    shutdown()
