import asyncio
import os
import random
import discord
from classes import User
from classes import AppManager
from classes.Systemlogger import logger
from os.path import join, dirname
from dotenv import load_dotenv

owners = ["212513828641046529"]
users = {}
app_path = "./apps/"


class MyClient(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.logger = None
        self.app_manager = None
        self.error = None
        self.delete_check = []
        self.useing = []
        self.add_point_user = []
        self.running = False
        self.system_ban_id = []

    async def using(self, message: discord.Message):
        self.useing.append(message.author.id)
        await asyncio.sleep(5)
        self.useing.remove(message.author.id)

    async def log(self, message: discord.Message):
        try:
            if not message.author.bot:
                if message.attachments and not message.author.bot:
                    await self.logger.send_image(message)
                elif "discord.gg" in message.content:
                    await self.logger.send_invite(message)
        except:
            pass

    async def point_task(self, message: discord.Message):
        if message.author.id in self.add_point_user:
            return
        user = get_user(message.author.id)
        if isinstance(user, bool):
            return
        user.add_point(random.randint(5, 15))
        self.add_point_user.append(message.author.id)
        await asyncio.sleep(60)
        self.add_point_user.remove(message.author.id)

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
        self.running = True
        try:
            with open('./logs/system_ban.txt', 'r') as f:
                text = f.read()
                for x in text.split(','):
                    self.system_ban_id.append(int(x))
        except:
            pass

    async def on_message(self, message: discord.Message):
        if not self.running:
            return
        await client.wait_until_ready()
        global users
        if message.author.id == 212513828641046529:
            if message.content == "sigma rc":
                await self.rc(message)
                return
            if message.content == "sigma clean":
                self.useing.clear()
                await message.channel.send("クリーン完了")
                return
            if message.content.startswith("sigma app reload"):
                await self.app_manager.logout()
                await self.app_manager.set_up()
                await message.channel.send("reload完了")
                return

        try:
            if await self.check(message):
                return
            self.loop.create_task(self.point_task(message))
            self.loop.create_task(self.using(message))
            if message.content == "sigma stop" and message.author.id == 212513828641046529:
                await self.app_manager.logout()
            # アプリコマンド
            data = await self.app_manager.catch_command(message, get_user(message.author.id).get_point())
            if not data == [False, False]:
                app, command = data[0], data[1]

                if app:
                    if not type(app) == bool:
                        if type(app) == int:
                            user = get_user(message.author.id)
                            user.add_point(app)
                        elif type(app) == str:
                            # print(app)
                            if app.startswith("ban "):
                                user_id = app.split()[1]
                                self.system_ban_id.append(int(user_id))
                            elif app.startswith("unban "):
                                user_id = app.split()[1]
                                self.system_ban_id.remove(int(user_id))
                    return True
                await self.logger.do_command(command=command, content=message.content,
                                             author_id=message.author.id, guild_id=message.guild.id,
                                             channel_id=message.channel.id, message=message)

            if message.content.startswith("sigma"):
                if not str(message.author.id) in users.keys():
                    await self.sigma_start(message)
                app = await self.load_os(message, get_user(message.author.id).get_point())
                if type(app) != bool:
                    if type(app) == int:
                        user = get_user(message.author.id)
                        user.add_point(app)
                    if type(app) == str:
                        if app == "apps":
                            await self.app_manager.show_apps(message)
                await self.logger.do_command(command="sigma", content=message.content,
                                             author_id=message.author.id, guild_id=message.guild.id,
                                             channel_id=message.channel.id, message=message)
                await self.app_manager.start(message)
            await self.app_manager.message_on(message)

        except:
            # import traceback
            # trace = traceback.format_exc()
            # await self.get_channel(497046680806621184).send(trace)
            raise

    async def on_member_join(self, member: discord.Member):
        await self.app_manager.member_join(member)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        await self.app_manager.reaction_add(reaction, user)

    async def on_member_remove(self, member: discord.Member):
        await self.app_manager.member_remove(member)

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

    async def load_os(self, message: discord.Message, point):
        return await self.app_manager.command(message, 'sigma', 'os', point)

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

    async def check(self, message: discord.Message):
        try:
            if not message.guild.me.guild_permissions.administrator:
                return True
        except:
            pass
        if message.author.id in self.system_ban_id:
            return True
        if message.author.bot:
            return True
        if message.author.id == client.user.id:
            return True
        if message.author.id in self.useing:
            return True

        return False

    def shutdown(self):
        with open('./logs/system_ban.txt', 'w') as f:
            text = ",".join([str(i) for i in self.system_ban_id])
            f.write(text)


def get_user(uid: int) -> User:
    if str(uid) in users.keys():
        return users[str(uid)]
    users[str(uid)] = User.User(uid, client)
    return users[str(uid)]


client = MyClient()

dotenv_path = join(dirname(__file__), '../sigma.env')
load_dotenv(dotenv_path)
client.run(os.environ.get("TOKEN"))
print(1)
client.shutdown()
