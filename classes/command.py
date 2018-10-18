import discord


class Command:
    def __init__(self, prefix, arguments):
        setattr(self, "prefix", prefix)
        setattr(self, "argument", arguments)
