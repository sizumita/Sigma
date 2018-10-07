import discord
from classes import sqlManager
manager = sqlManager.SQLManager(db="datas/sigma.db")


class User(object):
    def __init__(self, user_id: int, client: discord.Client):
        self.client = client
        self.sqluser = manager.get_user(user_id)
        self.point = manager.get_point(user_id)
        self.id = user_id
        self.mention = f"<@{user_id}>"
        self.user = client.get_user(user_id)
        self.avatar_url = self.user.avatar_url
        self.full = self.user.name + self.user.discriminator
        self.name = self.user.name

    def get_avater(self) -> str:
        return self.avatar_url

    def get_point(self) -> int:
        return self.point

    def add_point(self, point: int):
        self.point = manager.add_point(self.id, point)
        return self.get_point()
