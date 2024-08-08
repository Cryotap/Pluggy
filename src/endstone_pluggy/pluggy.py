import json
from endstone.plugin import *
from endstone import ColorFormat
from endstone.command import *
from endstone.form import *
from endstone.permissions import *
from endstone import Player
from endstone.event import *
from endstone.event import event_handler
import urllib.error
import urllib.response
import urllib.request
import sqlite3


class Pluggy(Plugin):
    cf = ColorFormat

    def on_load(self) -> None:
        self.logger.info("on_load is called!")

    def on_enable(self) -> None:
        self.logger.info("Enabled!!")
        self.register_events(self)
        con = sqlite3.connect('playgroups.db', timeout=3)
        cursor = con.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS pgroups (groups TEXT PRIMARY KEY, format TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS playgroups (player TEXT PRIMARY KEY, groups TEXT)")
        con.commit()
        con.close()

    def on_disable(self) -> None:
        self.logger.info("on_disable is called!")

    def applytags(self, msg, ha, player):
        colorss = str(ha).replace("&", "§")
        name = str(colorss).replace("{username}", str(player.name))
        dimension = name.replace("{dimension}", str(player.location.dimension.type.name))
        message = dimension.replace("{msg}", str(msg))
        return str(message)

    def checkingroup(self, user):
        con = sqlite3.connect('playgroups.db', timeout=3)
        cursor = con.cursor()
        rows = cursor.execute('select player from playgroups where player =?', (user,)).fetchall()
        con.commit()
        con.close()
        return rows

    def checkingroupname(self, user):
        con = sqlite3.connect('playgroups.db', timeout=3)
        cursor = con.cursor()
        rows = cursor.execute('select groups from playgroups where player =?', (user,)).fetchall()
        con.commit()
        con.close()
        return rows

    def checkingroupformat(self, group):
        con = sqlite3.connect('playgroups.db', timeout=3)
        cursor = con.cursor()
        rows = cursor.execute('select format from pgroups where groups =?', (group,)).fetchall()
        con.commit()
        con.close()
        return rows

    def listgroups(self):
        con = sqlite3.connect('playgroups.db', timeout=3)
        cursor = con.cursor()
        rows = cursor.execute('select groups from pgroups').fetchall()
        con.commit()
        con.close()
        return rows

    def listgroupedusers(self):
        con = sqlite3.connect('playgroups.db', timeout=3)
        cursor = con.cursor()
        rows = cursor.execute('select player from playgroups').fetchall()
        con.commit()
        con.close()
        return rows

    def checkgroup(self, group):
        con = sqlite3.connect('playgroups.db', timeout=3)
        cursor = con.cursor()
        rows = cursor.execute('select groups from pgroups where groups =?', (group,)).fetchall()
        con.commit()
        con.close()
        return rows

    def groupsadduser(self, us, data):
        if data is not None:
            d = json.loads(data)
            usr = str(d[0])
            group = str(d[1])
            con = sqlite3.connect('playgroups.db', timeout=3)
            cursor = con.cursor()
            cursor.execute('delete from playgroups where player =?', (usr,))
            cursor.execute("""INSERT INTO playgroups(player,groups) VALUES (?, ?)""", (usr, group))
            con.commit()
            con.close()
            us.send_message(f"{ColorFormat.GREEN}Done")
        else:
            us.send_message(f"{ColorFormat.RED}Missing Data")

    def groupsremovealluser(self, user):
        con = sqlite3.connect('playgroups.db', timeout=3)
        cursor = con.cursor()
        cursor.execute('drop table playgroups')
        cursor.execute("CREATE TABLE IF NOT EXISTS playgroups (player TEXT PRIMARY KEY, groups TEXT)")
        con.commit()
        con.close()
        user.send_message(f"{ColorFormat.RED}Removed all users!")

    def groupsremoveuser(self, us, data):
        if data is not None:
            userr = json.loads(data)
            usr = str(userr[0])
            con = sqlite3.connect('playgroups.db', timeout=3)
            cursor = con.cursor()
            cursor.execute('delete from playgroups where player =?', (usr,))
            con.commit()
            con.close()
            us.send_message(f"{ColorFormat.GREEN}Success!")

    def groupsaddformat(self, user, data):
        if data is not None:
            dat = json.loads(data)
            group = str(dat[1]).lower()
            formatss = str(dat[2])
            con = sqlite3.connect('playgroups.db', timeout=3)
            cursor = con.cursor()
            cursor.execute('delete from pgroups where groups =?', (group,))
            cursor.execute("""INSERT INTO pgroups(groups,format) VALUES (?, ?)""", (group, formatss))
            con.commit()
            con.close()
            user.send_message(f"{formatss}{ColorFormat.GREEN}has been added!")
        else:
            user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Group name please!")

    def groupsadd(self, user, data):
        if data is not None:
            dat = json.loads(data)
            con = sqlite3.connect('playgroups.db', timeout=3)
            cursor = con.cursor()
            cursor.execute('delete from pgroups where groups =?', (str(dat[0]).lower(),))
            cursor.execute("""INSERT INTO pgroups(groups) VALUES (?)""", (str(dat[0]).lower(),))
            con.commit()
            con.close()
            user.send_message(f"{ColorFormat.BLUE}{str(dat[0]).lower()}{ColorFormat.GREEN} has been added!")
        else:
            user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Group name please!")

    def groupsremove(self, user, data):
        if data is not None:
            dat = json.loads(data)
            con = sqlite3.connect('playgroups.db', timeout=3)
            cursor = con.cursor()
            cursor.execute('delete from pgroups where groups =?', (str(dat[0]).lower(),))
            con.commit()
            con.close()
            user.send_message(f"{ColorFormat.BLUE}{str(dat[0]).lower()}{ColorFormat.RED} has been removed!")
        else:
            user.send_message(f"{ColorFormat.MATERIAL_REDSTONE}Group name please!")

    def groupschangeformatform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Group Fomratter{ColorFormat.RESET}",
            controls=[
                Label(f"{ColorFormat.BLUE}" + "Tags: {msg}, {dimension}, {username}"),
                TextInput(placeholder="Group Name"),
                TextInput(placeholder="&l&e[{dimension}]&a[Helper]&r&a {username} &2> &a{msg}")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Change Format",
            on_submit=lambda player, data: self.groupsaddformat(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Group Fomratter Closed"
            ),
        )
        user.send_form(h)

    def groupsremoveuserform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}User Un-Grouper{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Player Nme")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Ungroup",
            on_submit=lambda player, data: self.groupsremoveuser(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Un-Grouper Closed"
            ),
        )
        user.send_form(h)

    def groupsadduserform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}User Grouper{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Player Name"),
                TextInput(placeholder="Group Name")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Add",
            on_submit=lambda player, data: self.groupsadduser(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Grouper Closed"
            ),
        )
        user.send_form(h)

    def groupsremoveform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Group Remover{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Group Nme (Don't use color color)")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Remove",
            on_submit=lambda player, data: self.groupsremove(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Group Remover Closed"
            ),
        )
        user.send_form(h)

    def groupsaddform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Group Adder{ColorFormat.RESET}",
            controls=[
                TextInput(placeholder="Group Name (Don't use color color)")
            ],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Add",
            on_submit=lambda player, data: self.groupsadd(user, data),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Group Adder Closed"
            ),
        )
        user.send_form(h)

    def groupslistform(self, user):
        h = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.MATERIAL_AMETHYST}Group List{ColorFormat.RESET}",
            controls=[],
            submit_button=f"{ColorFormat.MATERIAL_EMERALD}Done",
            on_submit=lambda player, data: player.send_message(""),
            on_close=lambda player: player.send_message(
                f"{ColorFormat.RED}Groups list closed"
            ),
        )
        for v in self.listgroups():
            a = str(v).strip("('',)")
            h.add_control(Label(a))
        user.send_form(h)

    @event_handler
    def chat_event(self, event: PlayerChatEvent):
        player = event.player
        usr = player.name
        msg = event.message
        if self.checkingroup(usr):
            e = self.checkingroup(usr)[0]
            e = str(e).strip("('',)")
            if e == usr:
                groupp = self.checkingroupname(usr)
                for v in self.listgroups():
                    a = str(v).strip("('',)")
                    b = str(groupp[0]).strip("('',)")
                    if a == b:
                        if self.checkgroup(b):
                            gformat = self.checkingroupformat(b)
                            gformat = str(gformat[0]).strip("('',)")
                            print(gformat)
                            newmessage = self.applytags(str(msg), str(gformat), player)
                            self.server.broadcast_message(newmessage)
                            event.cancelled = True

    name = "pluggy"
    prefix = "Pluggy"
    version = "0.1.1"
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
        "pluggy.experimental": {
            "description": "Allow users to look at the experimental features.",
            "default": True,
        },
        "pluggy.groups.addgroups": {
            "description": "Allow users to add groups.",
            "default": "op",
        },
        "pluggy.groups.removegroups": {
            "description": "Allow users to delete groups.",
            "default": "op",
        },
        "pluggy.groups.list": {
            "description": "Allow users to view all groups.",
            "default": True,
        },
        "pluggy.groups.adduser": {
            "description": "Allow users to add others to groups.",
            "default": "op",
        },
        "pluggy.groups.removeuser": {
            "description": "Allow users to remove others from groups.",
            "default": "op",
        },
        "pluggy.groupformat.change": {
            "description": "Allow users to change the group format.",
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
            if user.has_permission("pluggy.experimental"):
                self.experimentalform(user)

    def experimentalformcheck(self, user, sel):
        print(sel)
        if sel == 0:
            if user.has_permission("pluggy.plugin.donwload"):
                self.pdloadform(user)
        elif sel == 1:
            if user.has_permission("pluggy.groups.list"):
                self.groupslistform(user)
        elif sel == 2:
            if user.has_permission("pluggy.groups.addgroups"):
                self.groupsaddform(user)
        elif sel == 3:
            if user.has_permission("pluggy.groups.removegroups"):
                self.groupsremoveform(user)
        elif sel == 4:
            if user.has_permission("pluggy.groups.adduser"):
                self.groupsadduserform(user)
        elif sel == 5:
            if user.has_permission("pluggy.groups.removeuser"):
                self.groupsremoveuserform(user)
        elif sel == 6:
            if user.has_permission("pluggy.groups.removeuser"):
                self.groupsremovealluser(user)
        elif sel == 7:
            if user.has_permission("pluggy.groupformat.change"):
                self.groupschangeformatform(user)

    def experimentalform(self, uname, cf=cf):
        h = ActionForm(
            title=str(f"{cf.BOLD}{cf.MATERIAL_AMETHYST}Experimental Menu{cf.RESET}"),
            buttons=[
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Downloader{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/143830/download/png/128"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}List Groups{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/6083/download/png/128"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Add Group{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/5954/download/png/128"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Remove Group{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/6010/download/png/128"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Group User{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/48810/download/png/128"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Ungroup User{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/11372/download/png/48"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Ungroup All{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/11372/download/png/48"),
                ActionForm.Button(f"{cf.BOLD}{cf.LIGHT_PURPLE}Format Changer{cf.RESET}",
                                  icon="https://www.iconfinder.com/icons/9004725/download/png/512")
            ],
            on_submit=lambda player, selection: self.experimentalformcheck(uname, selection),
            on_close=lambda player: player.send_message(f"{ColorFormat.RED}Experimental Menu closed!"),
        )
        uname.send_form(h)

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
