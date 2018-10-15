import re
name_comp = re.compile(":name (.+)")


class Setting:
    def __init__(self, app_name: str):
        with open(f"./apps/{app_name}/settings.co", 'r') as f:
            data = f.readlines()

        dict_data = {
            "name": "",
            "version": "",
            "description": "",
        }

        for line in data:
            if re.match(name_comp, line):
                setattr(self, "name", re.match(name_comp, line).group(1))

        import discord.message
