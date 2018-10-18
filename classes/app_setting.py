import re
from classes.command import Command
name_comp = re.compile(":name (.+)")
ver_comp = re.compile(":ver (.+)")
desc_comp = re.compile(":desc (.+)")
command_comp = re.compile(":command (.+) $ (.+)")


class Setting:
    def __init__(self, app_name: str):
        with open(f"./apps/{app_name}/settings.co", 'r') as f:
            data = f.readlines()

        dict_data = {
            "name": "",
            "version": "",
            "description": "",
            "command": []
        }
        pointer = -1
        for line in data:
            pointer += 1
            name_match = re.match(name_comp, line)
            ver_match = re.match(ver_comp, line)
            desc_match = re.match(desc_comp, line)
            command_match = re.match(command_comp, line)
            if name_match:
                dict_data['name'] += name_match.groups()[0]
                continue
            if ver_match:
                dict_data['version'] += ver_match.groups()[0]
                continue
            if desc_match:
                dict_data['description'] += ver_match.groups()[0]
                continue
            if command_match:
                groups = command_match.groups()
                prefix = groups[0]
                arguments = groups[1].split()
                command_pointer = pointer + 1
