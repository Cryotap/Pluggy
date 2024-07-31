import json
from endstone.plugin import *
from endstone import ColorFormat
from endstone.command import *
from endstone.form import *
from endstone.permissions import *
from endstone import Player
import urllib.error
import urllib.response
import urllib.request


class Pluggy(Plugin):
    cf = ColorFormat

    def on_load(self) -> None:
        self.logger.info("on_load is called!")

    def on_enable(self) -> None:
        self.logger.info("on_enable is called!")

    def on_disable(self) -> None:
        self.logger.info("on_disable is called!")

    name = "pluggy"
    prefix = "Pluggy"
    version = "0.1.0"
    api_version = "0.5"
    description = "Python plugin manager for Endstone!"

    commands = {
        "pluggy": {
            "description": "Access the plugin manager form.",
            "usages": ["/pluggy"],
            "permissions": ["pluggy.command.use"],
        },
    }

    permissions = {
        "pluggy.command.use": {
            "description": "Allow users to use the plugin manager form.",
            "default": True,
        },
        "pluggy.list": {
            "description": "Allow users to use the plugin manager plugin list.",
            "default": True,
        },
        "pluggy.plugin.toggle": {
            "description": "Allow users to enable and disable plugins.",
            "default": "op",
        },
        "pluggy.plugin.download": {
            "description": "Allow users to download plugins.",
            "default": "op",
        },
        "pluggy.perms.list": {
            "description": "Allow users to list user perms.",
            "default": True,
        },
        "pluggy.perms.toggle": {
            "description": "Allow users to add and remove user perms.",
            "default": "op",
        },
    }

    def edplugs(self, user, data):
        if user.has_permission("pluggy.plugin.toggle"):
            if data is not None:
                plugs = self.server.plugin_manager.plugins
                for index, value in enumerate(json.loads(data)):
                    plugin = plugs[index]
                    print(plugin.name)
                    print(value)
                    if not value:
                        if self.server.plugin_manager.is_plugin_enabled(plugin):
                            self.server.plugin_manager.disable_plugin(plugin)
                            user.send_message(f"{ColorFormat.RED}Plugin {str(plugin.name)} is disabled!{ColorFormat.RESET}")
                    else:
                        if self.server.plugin_manager.is_plugin_enabled(plugin):
                            self.server.plugin_manager.enable_plugin(plugin)
                            user.send_message(f"{ColorFormat.MATERIAL_EMERALD}Plugin {str(plugin.name)} is enabled!{ColorFormat.RESET}")
            else:
                user.send_message(f"{ColorFormat.RED}Data missing!")
        else:
            user.send_message(f"{ColorFormat.RED}Permission pluggy.plugin.toggle is missing!")

    def plistform(self, user, cf=cf):
        plugs = self.server.plugin_manager.plugins
        h = ModalForm(
            title=f"{cf.BOLD}{cf.MATERIAL_NETHERITE}Plugins",
            controls=[],
            on_submit=lambda player, data: self.edplugs(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Plugin list closed"
            ),
        )
        for v in plugs:
            if self.server.plugin_manager.is_plugin_enabled(v):
                s = v.name
                h.add_control(Toggle(f"{ColorFormat.BLUE}" + str(s), default_value=True))
            else:
                h.add_control(Toggle(f"{ColorFormat.RED}" + str(v.name), default_value=False))
        user.send_form(h)

    def pload(self, user):
        user.send_message(f"{ColorFormat.MATERIAL_GOLD}Attempting to load...{ColorFormat.RESET}")
        self.server.plugin_manager.load_plugins("/plugins")
        user.send_message(f"{ColorFormat.MATERIAL_GOLD}Loaded Plugins!{ColorFormat.RESET}")

    def auperm(self, user, data):
        dat = json.loads(data)
        perm = str(dat[0])
        p = user
        t = self.server.get_player(str(dat[1]))
        if t is not None:
            if t.has_permission(perm):
                t.add_attachment(self, perm, True)
                p.send_message(f"{ColorFormat.MATERIAL_GOLD}Permission {perm} has been set!")
            else:
                p = self.server.get_player(user)
                p.send_message(f"{ColorFormat.RED}Permission {perm} is already set!")
        else:
            user.send_error_message("Please give a real user")

    def ruperm(self, user, data):
        dat = json.loads(data)
        perm = str(dat[0])
        p = user
        t = self.server.get_player(str(dat[1]))
        if t is not None:
            if t.has_permission(perm):
                t.add_attachment(self, perm, False)
                p.send_message(f"{ColorFormat.MATERIAL_GOLD}Permission {perm} has been removed!")
            else:
                p = self.server.get_player(user)
                p.send_message(f"{ColorFormat.RED}Permission {perm} is not assigned to Player!")
        else:
            user.send_error_message("Please give a online user")

    def aupermform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Add Permissions{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Permission"),
                TextInput(placeholder="Player")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Add",
            on_submit=lambda player, data: self.auperm(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Permission setter closed"
            ),
        )
        user.send_form(h)

    def luperms(self, user, info):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Permission List{ColorFormat.RESET}",
            controls=[],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Done",
            on_submit=lambda player, data: player.send_message(""),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Permission list closed"
            ),
        )
        us = json.loads(info)
        if self.server.get_player(str(us[0])) is not None:
            for v in self.server.get_player(str(us[0])).effective_permissions:
                h.add_control(Label(str(v.permission)))
            user.send_form(h)
        else:
            user.send_error_message("User doesn't exist")

    def rupermform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Permission Remover{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Permission"),
                TextInput(placeholder="Player")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Remove",
            on_submit=lambda player, data: self.ruperm(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Permission remover closed"
            ),
        )
        user.send_form(h)

    def lupermsform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Permission Lister{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Player")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Get List",
            on_submit=lambda player, data: self.luperms(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Permission finder closed"
            ),
        )
        user.send_form(h)

    def pdload(self, user, data):
        if data is not None and user.has_permission("pluggy.plugin.donwload"):
            # for gin in enumerate(json.loads(data)):
            gin = json.loads(data)
            if str(gin[2]) is not None:
                user.send_message(f"{ColorFormat.MATERIAL_GOLD}Downloading...")
                if str(gin[1]) is not None:
                    try:
                        ginn = f'https://github.com/{str(gin[2])}/{str(gin[0])}/releases/download/{gin[1]}/endstone_{gin[0]}-{gin[1]}-py2.py3-none-any.whl/'
                        dest = f'plugins\endstone_{gin[0]}-{gin[1]}-py2.py3-none-any.whl'
                        urllib.request.urlretrieve(ginn, dest)
                    except urllib.error.URLError as e:
                        user.send_message((str(e)))
                    else:
                        user.send_message(f"{ColorFormat.MATERIAL_GOLD}Done{ColorFormat.RESET}")
                else:
                    user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Please enter the version!")
            else:
                user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Please enter the author name!")
        else:
            user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Missing data!")

    def pdloadform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Plugin Downloader{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Joker"),
                TextInput(placeholder="0.1.1"),
                TextInput(placeholder="Cryotap")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Download",
            on_submit=lambda player, data: self.pdload(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Downloader Closed"
            ),
        )
        user.send_form(h)

    def penableform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Plugin Enabler{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Plugin Name")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Enable",
            on_submit=lambda player, data: self.penable(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Enabler Closed"
            ),
        )
        user.send_form(h)

    def pdisableform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Plugin Disabler{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Plugin Name")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Disable",
            on_submit=lambda player, data: self.pdisable(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Disabler Closed"
            ),
        )
        user.send_form(h)
        pass

    def penable(self, user, data):
        if data is not None:
            for dat in json.loads(data):
                if self.server.plugin_manager.get_plugin(str(dat)):
                    if not self.server.plugin_manager.is_plugin_enabled(str(dat)):
                        self.server.plugin_manager.enable_plugin(self.server.plugin_manager.get_plugin(str(dat)))
                        user.send_message(f"{ColorFormat.MATERIAL_GOLD}Plugin Enabled")
                    else:
                        user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Plugin is already enabled!")
                else:
                    user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Plugin not loaded!")
        else:
            user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Plugin name please!")

    def pdisable(self, user, data):
        if data is not None:
            for dat in json.loads(data):
                if self.server.plugin_manager.get_plugin(str(dat)):
                    if self.server.plugin_manager.is_plugin_enabled(str(dat)):
                        self.server.plugin_manager.disable_plugin(self.server.plugin_manager.get_plugin(str(dat)))
                        user.send_message(f"{ColorFormat.MATERIAL_GOLD}Plugin Disabled")
                    else:
                        user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Plugin is already disabled!")
                else:
                    user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Plugin is not loaded")
        else:
            user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Plugin name please!")

    def pmenable(self, user):
        self.server.plugin_manager.enable_plugins()
        user.send_message(f"{ColorFormat.MATERIAL_GOLD}Done!")

    def pmdisable(self, user):
        self.server.plugin_manager.disable_plugins()
        user.send_message(f"{ColorFormat.MATERIAL_GOLD}Done!")

    def mainformcheck(self, user, sel):
        print(sel)
        if sel == 0:
            if user.has_permission("pluggy.list"):
                self.plistform(user)
        elif sel == 1:
            if user.has_permission("pluggy.plugin.toggle"):
                self.pdisableform(user)
        elif sel == 2:
            if user.has_permission("pluggy.plugin.toggle"):
                self.penableform(user)
        elif sel == 3:
            if user.has_permission("pluggy.plugin.toggle"):
                self.pmdisable(user)
        elif sel == 4:
            if user.has_permission("pluggy.plugin.toggle"):
                self.pmenable(user)
        elif sel == 5:
            if user.has_permission("pluggy.plugin.toggle"):
                self.pload(user)
        elif sel == 6:
            if user.has_permission("pluggy.perms.list"):
                self.lupermsform(user)
        elif sel == 7:
            if user.has_permission("pluggy.perms.toggle"):
                self.aupermform(user)
        elif sel == 8:
            if user.has_permission("pluggy.perms.toggle"):
                self.rupermform(user)
        else:
            if user.has_permission("pluggy.plugin.toggle"):
                self.pdloadform(user)

    def mainnform(self, uname, cf=cf):
        h = ActionForm(
            title=str(f"{cf.BOLD}{cf.MATERIAL_AMETHYST}Pluggy Menu{cf.RESET}"),
            buttons=[
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Plugin List{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/3911247/download/png/512"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Plugin Disable{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/3911247/download/png/512"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Plugin Enable{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/3911247/download/png/512"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Plugin Mass Disable{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/3911247/download/png/512"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Plugin Mass Enable{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/3911247/download/png/512"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Plugin Mass Load{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/3911247/download/png/512"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}User Perms{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/285646/download/png/512"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Add User Perms{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/285646/download/png/512"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Remove User Perms{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/285646/download/png/512"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Experimental Features{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/7479649/download/png/512")
            ],
            on_submit=lambda player, selection: self.mainformcheck(uname, selection),
            on_close=lambda player: player.send_message(f"{ColorFormat.RED}Pluggy Menu closed!"),
        )
        uname.send_form(h)

    def on_command(self, sender: CommandSender, command: Command, args: list[str], cf=cf) -> bool:
        if command.name == "pluggy":
            if isinstance(sender, Player):
                self.mainnform(sender)
                return True
            else:
                sender.send_error_message(f"{cf.MATERIAL_REDSTONE}" + "You must be a player to run this command")
