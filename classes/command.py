import discord


class Command:
    def __init__(self, prefix, arguments, look, desc):
        self.prefix = prefix.replace("$ ", "")
        self.arguments = arguments
        self.look = look
        self.desc = desc

    def __str__(self):
        return self.prefix
