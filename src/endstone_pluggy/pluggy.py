from endstone.plugin import *
from endstone import ColorFormat
from endstone.command import *
from endstone.form import *
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
        "pluggy.subs": {
            "description": "Allow users to use the plugin manager form.",
            "default": False,
            "children": {
                "pluggy.command.use": True,
                "pluggy.list": True,
                "pluggy.plugin.toggle": "op",
                "pluggy.plugin.download": "op",
                "pluggy.perms.list": True,
                "pluggy.perms.toggle": "op",
            },
        },
    }

    def edplugs(self, user, data, plugs):
        if user.has_permission("pluggy.plugin.toggle"):
            for v in plugs:
                for d in data:
                    if not d:
                        if self.server.plugin_manager.is_plugin_enabled(str(v)):
                            self.server.plugin_manager.disable_plugin(v)
                            user.send_message(f"{ColorFormat.RED}Plugin {v} has been disabled!")
                    else:
                        if not self.server.plugin_manager.is_plugin_enabled(str(v)):
                            self.server.plugin_manager.enable_plugin(v)
                            user.send_message(f"{ColorFormat.RED}Plugin {v} has been enabled!")

    def plistform(self, user, cf=cf):
        plugs = self.server.plugin_manager.plugins
        h = ModalForm(
            title=f"{cf.BOLD}{cf.MATERIAL_NETHERITE}Plugins",
            controls=[],
            on_submit=lambda player, data: self.edplugs(user, data, plugs),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Plugin list closed"
            ),
        )
        for v in plugs:
            if self.server.plugin_manager.is_plugin_enabled(v):
                h.add_control(Toggle(f"{ColorFormat.BLUE}" + str(v), default_value=True))
            else:
                h.add_control(Toggle(f"{ColorFormat.RED}" + str(v), default_value=False))
        user.send_form(h)

    def pload(self, user):
        user.send_message(f"{ColorFormat.MATERIAL_GOLD}Attempting to load...{ColorFormat.RESET}")
        self.server.plugin_manager.load_plugins("/plugins")
        user.send_message(f"{ColorFormat.MATERIAL_GOLD}Loaded Plugins!{ColorFormat.RESET}")

    def auperm(self, user, data):
        perm = str(data[0])
        p = user
        t = self.server.get_player(str(data[1]))
        if not t.has_permission(perm):
            p.add_attachment(perm, True)
            p.send_message(f"{ColorFormat.MATERIAL_GOLD}Permission {perm} has been set!")
        else:
            p = self.server.get_player(user)
            p.send_message(f"{ColorFormat.RED}Permission {perm} is already set!")
        pass

    def ruperm(self, user, data):
        perm = str(data[0])
        p = user
        t = self.server.get_player(str(data[1]))
        if t.has_permission(perm):
            t.add_attachment(perm, False)
            p.send_message(f"{ColorFormat.MATERIAL_GOLD}Permission {perm} has been removed!")
        else:
            p = self.server.get_player(user)
            p.send_message(f"{ColorFormat.RED}Permission {perm} is not assigned to Player!")
        pass

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
        for v in info:
            h.add_control(Label(str(v)))
        user.send_form(h)

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
        if data[0]:
            if data[2]:
                user.send_message(f"{ColorFormat.MATERIAL_GOLD}Downloading...")
                try:
                    if data[1]:
                        url = "https://github.com/" + str(data[2]) + "/" + str(data[1]) + "/" + "endstone_" + str(data[0]).lower() + "-" + str(data(1)) + "-py2.py3-none-any.whl/"
                        urllib.request.urlretrieve(url, "plugins/" + "endstone_" + str(data[0]).lower() + "-" + str(data(1)) + "-py2.py3-none-any.whl/")
                    else:
                        user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Please enter the version!")
                except urllib.error.URLError as e:
                    user.send_error_message(str(e))
                    user.send_message(f"{ColorFormat.RED}Make sure the repo you are using has its tags formatted as the version\nfor example if it was version 0.1.0, it shouldn't say v0.1.0, it should say 0.1.0")
                else:
                    user.send_message(f"{ColorFormat.MATERIAL_EMERALD}Done! Please the delete the current version and then click Plugin Full Load!")
            else:
                user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Please enter the author name!")
        else:
            user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Please enter the plugin name!")

    def pdloadform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Plugin Downloader{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Plugin Name"),
                TextInput(placeholder="Version"),
                TextInput(placeholder="Author Name")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Download & Load",
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
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Download & Load",
            on_submit=lambda player, data: self.penable(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Downloader Closed"
            ),
        )
        user.send_form(h)

    def pdisableform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Plugin Disabler{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Plugin Name")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Download & Load",
            on_submit=lambda player, data: self.pdisable(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Downloader Closed"
            ),
        )
        user.send_form(h)
        pass

    def penable(self, user, data):
        if data[0]:
            if self.server.plugin_manager.get_plugin(data[0]):
                if not self.server.plugin_manager.is_plugin_enabled(data[0]):
                    self.server.plugin_manager.enable_plugin(data[0])
                    user.send_message(f"{ColorFormat.MATERIAL_GOLD}Plugin Enabled")
                else:
                    user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Plugin is already enabled!")
            else:
                user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Plugin not loaded!")
        else:
            user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Plugin name please!")

    def pdisable(self, user, data):
        if data[0]:
            if self.server.plugin_manager.get_plugin(data[0]):
                if self.server.plugin_manager.is_plugin_enabled(data[0]):
                    self.server.plugin_manager.disable_plugin(data[0])
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
        if sel == "Plugin List":
            if user.has_permission("pluggy.list"):
                self.plistform(user)
        elif sel == "Plugin Disable":
            if user.has_permission("pluggy.plugin.toggle"):
                self.pdisableform(user)
        elif sel == "Plugin Enable":
            if user.has_permission("pluggy.plugin.toggle"):
                self.penableform(user)
        elif sel == "Plugin Mass Disable":
            if user.has_permission("pluggy.plugin.toggle"):
                self.pmdisable(user)
        elif sel == "Plugin Mass Enable":
            if user.has_permission("pluggy.plugin.toggle"):
                self.pmenable(user)
        elif sel == "Plugin Mass Load":
            if user.has_permission("pluggy.plugin.toggle"):
                self.pload(user)
        elif sel == "Plugin Downloader":
            if user.has_permission("pluggy.plugin.download"):
                self.pdloadform(user)
        elif sel == "User Perms":
            if user.has_permission("pluggy.perms.list"):
                self.lupermsform(user)
        elif sel == "Add User Perms":
            if user.has_permission("pluggy.perms.toggle"):
                self.aupermform(user)
        elif sel == "Experimental Features":
            if user.has_permission("pluggy.plugin.toggle"):
                user.send_message(f"{ColorFormat.MATERIAL_IRON}Nothing to see yet!")
        else:
            if user.has_permission("pluggy.perms.toggle"):
                self.rupermform(user)

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
            on_submit=lambda player, selection: self.mainformcheck(uname, f"{selection}"),
            on_close=lambda player: player.send_message(f"{ColorFormat.RED}Pluggy Menu closed!"),
        )
        uname.send_form(h)

    def on_command(self, sender: CommandSender, command: Command, args: list[str], cf=cf) -> bool:
        if command.name == "pluggy":
            player = sender.as_player()
            if player is not None:
                p = self.server.get_player(sender)
                self.mainnform(p)
                return True
            else:
                sender.send_error_message(f"{cf.MATERIAL_REDSTONE}" + "You must be a player to run this command")
