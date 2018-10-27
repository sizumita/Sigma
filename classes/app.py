import re
from classes.command import Command
from importlib import machinery
name_comp = re.compile(":name (.+)")
ver_comp = re.compile(":ver (.+)")
desc_comp = re.compile(":desc (.+)")
command_comp_is_arg = re.compile(":command (.+) \$ (.+)")
command_comp = re.compile(":command (.+)")
command_look_comp = re.compile("\$look (.+)")
command_desc_comp = re.compile("\$desc (.+)")
permission_comp = re.compile(":per \[(.+)]")
continue_comp = re.compile(":continue (True|False)")


class App:
    __slots__ = ('dict_data', 'worker', 'instance', 'name',
                 'version', 'description', 'permission', 'command',
                 'is_continue',
                 )

    def __init__(self, app_name: str, client):
        with open(f"./apps/{app_name}/settings.co", 'r') as f:
            data = f.readlines()

        self.dict_data = {
            "name": "",
            "version": "",
            "description": "",
            "permission": [],
            "command": [],
            "is_continue": False,
        }
        pointer = -1
        for line in data:
            pointer += 1
            name_match = re.match(name_comp, line)
            ver_match = re.match(ver_comp, line)
            desc_match = re.match(desc_comp, line)
            permission_match = re.match(permission_comp, line)
            command_match = re.match(command_comp, line)
            continue_match = re.match(continue_comp, line)
            if name_match:
                self.dict_data['name'] += name_match.groups()[0]
                continue
            if ver_match:
                self.dict_data['version'] += ver_match.groups()[0]
                continue
            if desc_match:
                self.dict_data['description'] += desc_match.group(1).replace("\\", "\n")
                continue
            if permission_match:
                self.dict_data['permission'] += [int(i) for i in permission_match.groups()[0].split(",")]
                continue
            if continue_match:
                if continue_match.group(1) == "True":
                    self.dict_data['is_continue'] = True
                continue
            if command_match:
                groups = command_match.groups()
                prefix = groups[0]
                if re.match(command_comp_is_arg, line):
                    arguments = re.match(command_comp_is_arg, line).group(1).split()
                else:
                    arguments = []
                look = ""
                desc = ""
                command_pointer = pointer + 1
                for l in data[command_pointer:]:
                    look_match = re.match(command_look_comp, l)
                    desc_match = re.match(command_desc_comp, l)
                    if not l.startswith("$"):
                        break
                    if look_match:
                        look = look_match.group(0)
                        continue
                    if desc_match:
                        desc += desc_match.group(0).replace("\\", "\n")
                        continue
                _command = Command(prefix, arguments, look, desc, )
                self.dict_data["command"].append(_command)
        for key, value in self.dict_data.items():
            setattr(self, key, value)
        if self.is_continue:
            loader = machinery.SourceFileLoader(app_name, f"./apps/{app_name}/worker.py")
            app_module = loader.load_module()
            self.instance = app_module.Worker(client)
            self.worker = self.instance

    def __str__(self):
        return self.name

    def commands(self):
        return self.command

