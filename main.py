import asyncio
import ctypes
import io
import json
import os
import platform
import subprocess
import tempfile
import threading
import zipfile

import discord.errors
import numpy
import requests
from PIL import Image, ImageDraw
from PyQt5.QtGui import QIcon, QFontDatabase
from PyQt5.QtWidgets import QApplication, QMainWindow
from discord.ext import commands, tasks
from qasync import QEventLoop, asyncSlot

# noinspection PyUnresolvedReferences
import resources.icons
from resources.interface import *
from resources.updater import *

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("dankmemergrinder")
except:
    pass


class UpdaterWindow(QMainWindow):
    # noinspection PyShadowingNames
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon(resource_path("resources/icon.ico")))
        QFontDatabase.addApplicationFont(resource_path("fonts/Segoe.ttf"))
        self.ui = Ui_Updater()
        self.ui.setupUi(self)
        self.show()
        self.ui.changelog_label.setText(
            requests.get(
                "https://api.github.com/repos/BridgeSenseDev/Dank-Memer-Grinder/releases"
            )
            .json()[0]["body"]
            .replace("## ", "")
            .replace("* ", "• ")
        )
        self.ui.update_btn.clicked.connect(self.update)
        self.ui.skip_btn.clicked.connect(self.skip)

    def update(self):
        self.close()
        match platform.system():
            case "Windows":
                r = requests.get(
                    "https://github.com/BridgeSenseDev/Dank-Memer-Grinder/blob/main/"
                    "updater/Windows-amd64.exe?raw=true",
                    stream=True,
                )
                open("Windows-amd64.exe", "wb").write(r.content)
                subprocess.Popen("./Windows-amd64.exe")
            case "Linux":
                if platform.machine() == "aarch64":
                    r = requests.get(
                        "https://github.com/BridgeSenseDev/Dank-Memer-Grinder/releases/download/v"
                        f"{version}/Dank-Memer-Grinder-v{version}-Linux-arm64.zip",
                        stream=True,
                    )
                    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                        with open("Dank Memer Grinder", "wb") as f:
                            f.write(z.read("Dank Memer Grinder"))
                    subprocess.Popen("./Dank Memer Grinder")
                else:
                    r = requests.get(
                        "https://github.com/BridgeSenseDev/Dank-Memer-Grinder/releases/download/v"
                        f"{version}/Dank-Memer-Grinder-v{version}-Linux-amd64.zip",
                        stream=True,
                    )
                    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                        with open("Dank Memer Grinder", "wb") as f:
                            f.write(z.read("Dank Memer Grinder"))
                    subprocess.Popen("./Dank Memer Grinder")
            case "Darwin":
                r = requests.get(
                    "https://github.com/BridgeSenseDev/Dank-Memer-Grinder/releases/download/v"
                    f"{version}/Dank-Memer-Grinder-v{version}-Darwin-amd64.zip",
                    stream=True,
                )
                with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                    with open("Dank Memer Grinder", "wb") as f:
                        f.write(z.read("Dank Memer Grinder"))
                subprocess.Popen("./Dank Memer Grinder")
        sys.exit(os._exit(0))

    def skip(self):
        self.close()
        window.show()


def update():
    global config_dict
    threading.Timer(5, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)


update()


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        # noinspection PyProtectedMember
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


async def start_bot(token, account_id):
    class MyClient(commands.Bot):
        def __init__(self):
            super().__init__(command_prefix="-", self_bot=True)
            self.config_dict = config_dict
            self.window = window
            self.account_id = account_id
            self.channel_id = int(config_dict[account_id]["channel_id"])
            self.channel = None
            self.commands_list = {
                "trivia": "trivia",
                "dig": "dig",
                "fish": "fish",
                "hunt": "hunt",
                "pm": "postmemes",
                "beg": "beg",
                "hl": "highlow",
                "search": "search",
                "dep_all": "deposit",
                "stream": "stream",
                "work": "work",
                "daily": "daily",
                "bj": "blackjack",
            }
            self.commands_delay = {
                "trivia": 10,
                "dig": 40,
                "fish": 40,
                "hunt": 40,
                "pm": 50,
                "beg": 45,
                "hl": 30,
                "search": 30,
                "dep_all": 60,
                "stream": 660,
                "work": 3600,
                "daily": 86400,
            }
            # Add delay to commands
            for command in self.commands_delay:
                self.commands_delay[command] = int(self.commands_delay[command] * 1.1)
            self.last_ran = {}
            for command in self.commands_list:
                self.last_ran[command] = 0

        @tasks.loop(seconds=5)
        async def update(self):
            with open("config.json", "r") as config_file:
                self.config_dict = json.load(config_file)

        @staticmethod
        async def click(message, component, children):
            try:
                await message.components[component].children[children].click()
            except (discord.errors.HTTPException, discord.errors.InvalidData):
                pass

        @staticmethod
        async def select(message, component, children, option):
            try:
                select_menu = message.components[component].children[children]
                await select_menu.choose(select_menu.options[option])
            except (discord.errors.HTTPException, discord.errors.InvalidData):
                pass

        async def send(self, command_name, channel=None, **kwargs):
            if channel is None:
                channel = self.channel
                async for cmd in channel.slash_commands(query=command_name, limit=None):
                    try:
                        if cmd.application.id == 270904126974590976:
                            await cmd(**kwargs)
                    except (discord.errors.DiscordServerError, KeyError):
                        pass
                    return

        async def sub_send(
            self, command_name, sub_command_name, channel=None, **kwargs
        ):
            if channel is None:
                channel = self.channel
            try:
                async for cmd in channel.slash_commands(query=command_name, limit=None):
                    if cmd.application.id == 270904126974590976:
                        for count, sub_cmd in enumerate(cmd.children):
                            if sub_cmd.name.lower() == sub_command_name.lower():
                                await cmd.children[count](**kwargs)
                                break
                        return
            except (discord.errors.DiscordServerError, KeyError):
                pass

        async def setup_hook(self):
            self.update.start()
            self.channel = await self.fetch_channel(self.channel_id)
            if getattr(window.ui, f"account_btn_{account_id}").text() != "Logging In":
                return
            getattr(window.ui, f"output_text_{self.account_id}").append(
                f"Logged in as {self.user}"
            )
            getattr(window.ui, f"account_btn_{account_id}").setText(
                f"{self.user.name}\n#{self.user.discriminator}"
            )
            with tempfile.TemporaryDirectory() as dirpath:
                path = os.path.join(dirpath, f"account_{account_id}")
                await self.user.avatar.save(path)

                # Convert image to circle
                img = Image.open(path).convert("RGB")
                height, width = img.size
                lum_img = Image.new("L", (height, width), 0)

                draw = ImageDraw.Draw(lum_img)
                draw.pieslice(
                    ((0, 0), (height, width)), 0, 360, fill=255, outline="white"
                )
                img_arr = numpy.array(img)
                lum_img_arr = numpy.array(lum_img)
                final_img_arr = numpy.dstack((img_arr, lum_img_arr))
                Image.fromarray(final_img_arr).save(f"{path}.png")

                getattr(self.window.ui, f"account_btn_{account_id}").setIcon(
                    QIcon(f"{path}.png")
                )
                getattr(self.window.ui, f"account_btn_{account_id}").setIconSize(
                    QtCore.QSize(35, 35)
                )

            await self.load_extension("cogs.trivia")
            await self.load_extension("cogs.pm")
            await self.load_extension("cogs.hl")
            await self.load_extension("cogs.search")
            await self.load_extension("cogs.stream")
            await self.load_extension("cogs.minigames")
            await self.load_extension("cogs.autobuy")
            await self.load_extension("cogs.blackjack")
            await self.load_extension("cogs.commands")

    await MyClient().start(token)


class MainWindow(QMainWindow):
    # noinspection PyShadowingNames
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon(resource_path("resources/icon.ico")))
        QFontDatabase.addApplicationFont(resource_path("resources/fonts/Segoe.ttf"))
        QFontDatabase.addApplicationFont(resource_path("resources/fonts/Impact.ttf"))
        self.ui = Ui_DankMemerGrinder()
        self.ui.setupUi(self)
        self.account_id = "1"
        config_dict.update({"state": False})
        with open("config.json", "w") as file:
            json.dump(config_dict, file, ensure_ascii=False, indent=4)
        if config_dict[self.account_id]["state"] is False:
            self.ui.toggle.setStyleSheet("background-color : #d83c3e")
            self.ui.toggle.setText(f"Bot {self.account_id} Disabled")
        else:
            self.ui.toggle.setStyleSheet("background-color : #2d7d46")
            self.ui.toggle.setText(f"Bot {self.account_id} Enabled")
            getattr(self.ui, f"output_text_{self.account_id}").append(
                f"Started Bot {self.account_id}"
            )
        self.ui.toggle.clicked.connect(lambda: self.check())

        # Sidebar
        sidebar_buttons = ["home", "settings", "commands", "auto_buy", "gambling"]
        for button in sidebar_buttons:
            getattr(self.ui, f"{button}_btn").clicked.connect(
                lambda checked, button=button: self.sidebar(
                    getattr(self.ui, f"{button}_btn"),
                    getattr(self.ui, f"{button}_widget_{self.account_id}"),
                )
            )

        # Initialize settings
        for account_id in map(str, range(1, 6)):
            getattr(self.ui, f"output_text_{account_id}").setVerticalScrollBar(
                getattr(self.ui, f"output_scrollbar_{account_id}")
            )
            getattr(self.ui, f"blackjack_checkbox_{account_id}").setChecked(
                config_dict[account_id]["commands"]["bj"]["state"]
            )
            getattr(self.ui, f"multi_amount_{account_id}").setText(
                str(config_dict[account_id]["commands"]["bj"]["multi"])
            )
            getattr(self.ui, f"blackjack_amount_{account_id}").setText(
                str(config_dict[account_id]["commands"]["bj"]["bj_amount"])
            )
            getattr(self.ui, f"lifesavers_checkbox_{account_id}").setChecked(
                config_dict[account_id]["autobuy"]["lifesavers"]["state"]
            )
            getattr(self.ui, f"lifesavers_amount_{account_id}").setValue(
                config_dict[account_id]["autobuy"]["lifesavers"]["amount"]
            )
            getattr(self.ui, f"token_input_{account_id}").setText(
                config_dict[account_id]["discord_token"]
            )
            getattr(self.ui, f"channel_input_{account_id}").setText(
                config_dict[account_id]["channel_id"]
            )
            getattr(self.ui, f"trivia_chance_{account_id}").setValue(
                int(config_dict[account_id]["trivia_correct_chance"] * 100)
            )

            for command in config_dict[account_id]["commands"]:
                try:
                    getattr(self.ui, f"{command}_checkbox_{account_id}").setChecked(
                        config_dict[account_id]["commands"][command]
                    )
                except AttributeError:
                    pass

            for autobuy in config_dict[account_id]["autobuy"]:
                try:
                    getattr(self.ui, f"{autobuy}_checkbox_{account_id}").setChecked(
                        config_dict[account_id]["autobuy"][autobuy]
                    )
                except (TypeError, AttributeError):
                    pass

            # Commands
            command_buttons = [
                "trivia",
                "dig",
                "fish",
                "hunt",
                "pm",
                "beg",
                "hl",
                "search",
                "dep_all",
                "stream",
                "work",
                "daily",
            ]
            for button in command_buttons:
                getattr(self.ui, f"{button}_checkbox_{account_id}").clicked.connect(
                    lambda checked, account_id=account_id, button=button: self.commands(
                        button,
                        getattr(self.ui, f"{button}_checkbox_{account_id}").isChecked(),
                    )
                )
            getattr(self.ui, f"start_btn_{account_id}").clicked.connect(
                lambda: self.toggle_all(True)
            )
            getattr(self.ui, f"stop_btn_{account_id}").clicked.connect(
                lambda: self.toggle_all(False)
            )

            # Autobuy
            autobuy_buttons = ["lifesavers", "fishing", "shovel", "rifle"]
            for button in autobuy_buttons:
                getattr(self.ui, f"{button}_checkbox_{account_id}").clicked.connect(
                    lambda checked, account_id=account_id, button=button: self.autobuy(
                        button,
                        getattr(self.ui, f"{button}_checkbox_{account_id}").isChecked(),
                        "state",
                    )
                )
            getattr(self.ui, f"lifesavers_amount_{account_id}").valueChanged.connect(
                lambda checked, account_id=account_id: self.autobuy(
                    "lifesavers",
                    getattr(self.ui, f"lifesavers_amount_{account_id}").value(),
                    "amount",
                )
            )

            # Blackjack
            getattr(self.ui, f"blackjack_checkbox_{account_id}").clicked.connect(
                lambda checked, account_id=account_id: self.blackjack(
                    "state",
                    getattr(self.ui, f"blackjack_checkbox_{account_id}").isChecked(),
                )
            )
            getattr(self.ui, f"multi_amount_{account_id}").textChanged.connect(
                lambda checked, account_id=account_id: self.blackjack(
                    "multi", int(getattr(self.ui, f"multi_amount_{account_id}").text())
                )
            )
            getattr(self.ui, f"blackjack_amount_{account_id}").textChanged.connect(
                lambda checked, account_id=account_id: self.blackjack(
                    "bj_amount",
                    getattr(self.ui, f"blackjack_amount_{account_id}").text(),
                )
            )

            # Settings buttons
            getattr(self.ui, f"token_input_{account_id}").textChanged.connect(
                lambda checked, account_id=account_id: self.settings(
                    "token", getattr(self.ui, f"token_input_{account_id}").text()
                )
            )
            getattr(self.ui, f"channel_input_{account_id}").textChanged.connect(
                lambda checked, account_id=account_id: self.settings(
                    "channel", getattr(self.ui, f"channel_input_{account_id}").text()
                )
            )
            getattr(self.ui, f"trivia_chance_{account_id}").valueChanged.connect(
                lambda checked, account_id=account_id: self.settings(
                    "trivia_chance",
                    getattr(self.ui, f"trivia_chance_{account_id}").value(),
                )
            )

            # Account buttons
            getattr(self.ui, f"account_btn_{account_id}").clicked.connect(
                lambda checked, account_id=account_id: self.accounts(
                    getattr(self.ui, f"account_btn_{account_id}"),
                    getattr(self.ui, f"account_widget_{account_id}"),
                )
            )

    @asyncSlot()
    async def check(self):
        if config_dict[self.account_id]["state"] is False:
            config_dict[self.account_id].update({"state": True})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
            self.ui.toggle.setStyleSheet("background-color : #2d7d46")
            self.ui.toggle.setText(f"Bot {self.account_id} Enabled")
            getattr(self.ui, f"output_text_{self.account_id}").append(
                f"Started Bot {self.account_id}"
            )
        else:
            config_dict[self.account_id].update({"state": False})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
            self.ui.toggle.setStyleSheet("background-color : #d83c3e")
            self.ui.toggle.setText(f"Bot {self.account_id} Disabled")
            getattr(self.ui, f"output_text_{self.account_id}").append(
                f"Stopped Bot {self.account_id}"
            )

    @asyncSlot()
    async def sidebar(self, button, widget):
        buttons = [
            self.ui.home_btn,
            self.ui.settings_btn,
            self.ui.commands_btn,
            self.ui.auto_buy_btn,
            self.ui.gambling_btn,
        ]
        for i in buttons:
            if i == button:
                button.setStyleSheet("background-color: #5865f2")
            else:
                i.setStyleSheet("background-color: #42464d")
        getattr(self.ui, f"main_menu_widget_{self.account_id}").setCurrentWidget(widget)

    @asyncSlot()
    async def accounts(self, button, widget):
        buttons = [
            self.ui.account_btn_1,
            self.ui.account_btn_2,
            self.ui.account_btn_3,
            self.ui.account_btn_4,
            self.ui.account_btn_5,
        ]
        for count, i in enumerate(buttons):
            if i == button:
                button.setStyleSheet("background-color: #5865f2")
                self.account_id = str(count + 1)
                if config_dict[self.account_id]["state"] is False:
                    self.ui.toggle.setStyleSheet("background-color : #d83c3e")
                    self.ui.toggle.setText(f"Bot {self.account_id} Disabled")
                else:
                    self.ui.toggle.setStyleSheet("background-color : #2d7d46")
                    self.ui.toggle.setText(f"Bot {self.account_id} Enabled")
            else:
                i.setStyleSheet("background-color: #42464d")
        self.ui.main_menu_widget.setCurrentWidget(widget)
        current_widget = getattr(
            self.ui, f"main_menu_widget_{self.account_id}"
        ).currentWidget()
        await self.sidebar(
            getattr(self.ui, f"{current_widget.objectName()[:-9]}_btn"), current_widget
        )

    @asyncSlot()
    async def commands(self, command, state):
        config_dict[self.account_id]["commands"].update({command: state})
        with open("config.json", "w") as file:
            json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def toggle_all(self, state):
        for command in config_dict[self.account_id]["commands"]:
            if command != "bj":
                getattr(self.ui, f"{command}_checkbox_{self.account_id}").setChecked(
                    state
                )
                config_dict[self.account_id]["commands"].update({command: state})
                with open("config.json", "w") as file:
                    json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def blackjack(self, command, state):
        config_dict[self.account_id]["commands"]["bj"].update({command: state})
        with open("config.json", "w") as file:
            json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def autobuy(self, item, state, command=None):
        if item == "lifesavers":
            config_dict[self.account_id]["autobuy"][item].update({command: state})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        else:
            config_dict[self.account_id]["autobuy"][item] = state
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def settings(self, command, state):
        if command == "channel":
            config_dict[self.account_id].update({"channel_id": state})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        elif command == "token":
            config_dict[self.account_id].update({"discord_token": state})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
            if config_dict[self.account_id]["discord_token"] != "":
                threading.Thread(
                    target=between_callback,
                    args=(
                        config_dict[self.account_id]["discord_token"],
                        self.account_id,
                    ),
                ).start()
            else:
                getattr(window.ui, f"account_btn_{self.account_id}").setText(
                    f"Account {self.account_id}"
                )
                icon = QtGui.QIcon()
                icon.addPixmap(
                    QtGui.QPixmap(":/icons/icons/user.svg"),
                    QtGui.QIcon.Mode.Normal,
                    QtGui.QIcon.State.Off,
                )
                getattr(window.ui, f"account_btn_{self.account_id}").setIcon(icon)
        elif command == "trivia_chance":
            config_dict[self.account_id].update(
                {"trivia_correct_chance": int(state) / 100}
            )
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)


def between_callback(token, account_id):
    getattr(window.ui, f"account_btn_{account_id}").setText("Logging In")
    icon = QtGui.QIcon()
    icon.addPixmap(
        QtGui.QPixmap(":/icons/icons/loader.svg"),
        QtGui.QIcon.Mode.Normal,
        QtGui.QIcon.State.Off,
    )
    getattr(window.ui, f"account_btn_{account_id}").setIcon(icon)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(start_bot(token, account_id))
    except discord.errors.LoginFailure:
        getattr(window.ui, f"account_btn_{account_id}").setText("Invalid Token")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/alert-triangle.svg"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        getattr(window.ui, f"account_btn_{account_id}").setIcon(icon)
        getattr(window.ui, f"account_btn_{account_id}")
    loop.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    version = requests.get(
        "https://raw.githubusercontent.com/BridgeSenseDev/Dank-Memer-Grinder/main/"
        "resources/version.txt"
    ).text
    window = MainWindow()
    if int(version.replace(".", "")) > 110:
        updater = UpdaterWindow()
    else:
        window.show()
    for account_id in map(str, range(1, 6)):
        if config_dict[account_id]["discord_token"] != "":
            threading.Thread(
                target=between_callback,
                args=(config_dict[account_id]["discord_token"], account_id),
            ).start()
        else:
            getattr(window.ui, f"account_btn_{account_id}").setText(
                f"Account {account_id}"
            )
            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap(":/icons/icons/user.svg"),
                QtGui.QIcon.Mode.Normal,
                QtGui.QIcon.State.Off,
            )
            getattr(window.ui, f"account_btn_{account_id}").setIcon(icon)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    loop.run_forever()
    # noinspection PyProtectedMember
    sys.exit(os._exit(0))
