import discord
import yaml
import re
from importlib import machinery
import os
# from main import MyClient
app_path = "./apps/"


async def send(to: discord.TextChannel, message):
    await to.send(f"```\n{message}\n```")


class AppManager(object):
    def __init__(self, client: discord.Client):
        self.client = client
        self.app_list = []
        self.continue_app = {}
        self.commands = []
        self._commands = {}

    async def set_up(self):
        self.app_list = [file for file in os.listdir(app_path) if os.path.isdir(app_path + file)]
        for app_name in self.app_list:
            a_path = app_path + app_name + "/data/config.yml"
            with open(a_path, 'r') as f:
                data = yaml.load(f)
            if data["continue"]:
                loader = machinery.SourceFileLoader(app_name, app_path + app_name + '/worker.py')
                app_module = loader.load_module()
                instance = app_module.Worker(self.client)
                self.continue_app[app_name] = instance
            self.commands += data["commands"]
            for x in data["commands"]:
                self._commands[x] = app_name

    async def show_apps(self, message: discord.Message):
        content = message.content
        author = message.author
        channel = message.channel
        guild = message.guild
        await send(channel, "Sigma CUI APPSへ、ようこそ。")
        text = """Sigma CUI APPS\n\napps:\n\n"""
        try:
            for dirname in self.app_list:
                with open(app_path + dirname + "/data/config.yml", 'r+') as f:
                    data = yaml.load(f)
                    description = data['description']
                text += "sigma {0} -> {1}\n\n".format(dirname, description)

        except Exception as e:
            await send(channel, "APP 読み込み中にエラーが発生しました。")
            import traceback
            await send(channel, e.args)
            return False

        text += "commands:\n\nsigma menu -> menu画面にもどります。"

        await send(channel, text)
        return True

    async def start(self, message: discord.Message):
        content = message.content
        app_name = re.sub("[sigma ]", "", content, 6)
        if not app_name in self.app_list:
            # await send(channel, "そのようなアプリはありません。")
            return False
        if app_name in self.continue_app.keys():
            await self.continue_app[app_name].join(message)
            return True
        loader = machinery.SourceFileLoader(app_name, app_path + app_name + '/worker.py')
        my_module = loader.load_module()
        instance = my_module.Worker(self.client)
        await instance.join(message)

    async def command(self, message: discord.Message, command: str, app: str):
        if not message.content == command:
            args = re.sub("[{}]".format(command), "", message.content, len(command))
        else:
            args = ""
        if app in self.continue_app.keys():
            try:
                if args:
                    if args.split()[0] == "help":
                        return await self.continue_app[app].join(message)

                return await self.continue_app[app].command(message, command, args.split())
            except IndexError:
                return False
        loader = machinery.SourceFileLoader(app, app_path + app + '/worker.py')
        app_module = loader.load_module()
        instance = app_module.Worker(self.client)
        if args:
            if args.split()[0] == "help":
                await instance.join(message)
        try:
            return await instance.command(message, command, args.split())
        except IndexError:
            return False

    async def do_loop(self, counter: int) -> bool:
        for key, value in self.continue_app.items():
            try:
                await value.loop(counter, self.client)
            except AttributeError:
                pass
        return True

    async def message_on(self, message: discord.Message):
        for key, value in self.continue_app.items():
            try:
                await value.on_message(message)
            except AttributeError:
                raise

    async def member_join(self, member: discord.Member):
        for key, value in self.continue_app.items():
            try:
                await value.member_join(member)
            except AttributeError:
                raise

    async def member_remove(self, member: discord.Member):
        for key, value in self.continue_app.items():
            try:
                await value.member_remove(member)
            except AttributeError:
                raise

    async def catch_command(self, message: discord.Message):
        for x in self.commands:
            if message.content.startswith(x):
                return [await self.command(message, x, self._commands[x]), self._commands[x]]
        return [False, False]

    async def logout(self):
        for key, value in self.continue_app.items():
            try:
                await value.logout()
            except AttributeError:
                pass
        return True
