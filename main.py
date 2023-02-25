import asyncio
import ctypes
import io
import json
import os
import platform
import stat
import subprocess
import sys
import tempfile
import threading
import zipfile
from pathlib import Path

import discord.errors
import numpy
import requests
from discord.ext import commands, tasks
from PIL import Image, ImageDraw
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QFontDatabase, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
from qasync import QEventLoop, asyncSlot

import resources.icons
from resources.interface import *
from resources.load_account import load_account
from resources.updater import *

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("dankmemergrinder")
except AttributeError:
    pass


class UpdaterWindow(QMainWindow):
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
                    (
                        "https://github.com/BridgeSenseDev/Dank-Memer-Grinder/blob/"
                        "main/updater/Windows-amd64.exe?raw=true"
                    ),
                    stream=True,
                )
                temp_file = os.path.join(tempfile.gettempdir(), "Windows-amd64.exe")
                with open(temp_file, "wb") as f:
                    f.write(r.content)
                subprocess.Popen(temp_file)
                sys.exit(os._exit(0))
            case "Linux":
                if platform.machine() == "aarch64":
                    arch = "Linux-arm64"
                else:
                    arch = "Linux-amd64"
            case "Darwin":
                arch = "Darwin-amd64"
        r = requests.get(
            (
                "https://github.com/BridgeSenseDev/Dank-Memer-Grinder/blob/main/"
                f"updater/{arch}?raw=true"
            ),
            stream=True,
        )
        temp_file = os.path.join(tempfile.gettempdir(), arch)
        with open(temp_file, "wb") as f:
            f.write(r.content)
        os.chmod(temp_file, os.stat(temp_file).st_mode | 0o111)
        subprocess.Popen(temp_file)
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
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


async def start_bot(token, account_id):
    class MyClient(commands.Bot):
        def __init__(self):
            super().__init__(command_prefix="-", self_bot=True)
            self.window = window
            self.account_id = account_id
            self.config_dict = config_dict[self.account_id]
            self.state = self.config_dict["state"]
            self.channel_id = int(config_dict[account_id]["channel_id"])
            self.channel = None
            self.commands_list = {
                "trivia": "trivia",
                "dig": "dig",
                "fish": "fish",
                "hunt": "hunt",
                "pm": "postmemes",
                "beg": "beg",
                "pet": "pets",
                "hl": "highlow",
                "search": "search",
                "dep_all": "deposit",
                "stream": "stream",
                "work": "work",
                "daily": "daily",
                "crime": "crime",
            }
            self.commands_delay = {
                "trivia": 10,
                "dig": 40,
                "fish": 40,
                "hunt": 40,
                "pm": 50,
                "beg": 45,
                "pet": 1800,
                "hl": 30,
                "search": 30,
                "dep_all": 60,
                "stream": 660,
                "work": 3600,
                "daily": 86400,
                "crime": 50,
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
                self.config_dict = json.load(config_file)[self.account_id]
                self.state = self.config_dict["state"]

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
                    except (
                        discord.errors.DiscordServerError,
                        KeyError,
                        discord.errors.InvalidData,
                    ):
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
            except (
                discord.errors.DiscordServerError,
                KeyError,
                discord.errors.InvalidData,
            ):
                pass

        async def setup_hook(self):
            self.update.start()
            self.channel = await self.fetch_channel(self.channel_id)
            if (
                getattr(window.ui, f"account_btn_{self.account_id}").text()
                != "Logging In"
            ):
                return
            self.window.output.emit(
                [f"output_text_{self.account_id}", f"Logged in as {self.user}"]
            )
            getattr(window.ui, f"account_btn_{account_id}").setText(
                f"{self.user.name}\n#{self.user.discriminator}"
            )
            with tempfile.TemporaryDirectory() as dirpath:
                path = os.path.join(dirpath, f"account_{account_id}")
                await self.user.display_avatar.save(path)

                # Convert image to circle
                img = Image.open(path).convert("RGB")
                height, width = img.size
                lum_img = Image.new("L", (height, width), 0)

                draw = ImageDraw.Draw(lum_img)
                draw.pieslice(
                    ((0, 0), (height, width)), 0, 360, fill=255, outline="white"
                )
                # noinspection PyTypeChecker
                img_arr = numpy.array(img)
                # noinspection PyTypeChecker
                lum_img_arr = numpy.array(lum_img)
                final_img_arr = numpy.dstack((img_arr, lum_img_arr))
                Image.fromarray(final_img_arr).save(f"{path}.png")

                getattr(self.window.ui, f"account_btn_{account_id}").setIcon(
                    QIcon(f"{path}.png")
                )
                getattr(self.window.ui, f"account_btn_{account_id}").setIconSize(
                    QtCore.QSize(35, 35)
                )

            for filename in os.listdir(resource_path("./cogs")):
                if filename.endswith(".py"):
                    await self.load_extension(f"cogs.{filename[:-3]}")

    try:
        await MyClient().start(token)
    except discord.errors.LoginFailure:
        getattr(window.ui, f"account_btn_{account_id}").setText("Invalid Token")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/warning.png"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        getattr(window.ui, f"account_btn_{account_id}").setIcon(icon)
    except (discord.errors.NotFound, ValueError):
        getattr(window.ui, f"account_btn_{account_id}").setText("Invalid Channel")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/warning.png"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        getattr(window.ui, f"account_btn_{account_id}").setIcon(icon)


class Stream(QtCore.QObject):
    new_text = QtCore.pyqtSignal(str)

    def write(self, text):
        self.new_text.emit(str(text))


class MainWindow(QMainWindow):
    output = pyqtSignal(list)

    def __init__(self):
        global config_dict
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon(resource_path("resources/icon.ico")))
        self.setWindowTitle("Dank Memer Grinder")

        QFontDatabase.addApplicationFont(resource_path("resources/fonts/Segoe.ttf"))
        QFontDatabase.addApplicationFont(resource_path("resources/fonts/Impact.ttf"))
        self.ui = Ui_DankMemerGrinder(len(config_dict) + 1)
        self.ui.setupUi(self)

        # Initialize settings
        for account_id in range(1, len(config_dict) + 1):
            if str(account_id) not in config_dict:
                config_dict = {
                    k: v
                    for i, (k, v) in enumerate(config_dict.items())
                    if i != account_id - 1
                }
                with open("config.json", "w") as file:
                    json.dump(config_dict, file, ensure_ascii=False, indent=4)
                continue
            load_account(self, str(account_id))
        # noinspection PyArgumentList
        sys.stdout = Stream(new_text=self.onUpdateText)
        # noinspection PyArgumentList
        sys.stderr = Stream(new_text=self.onUpdateText)
        self.output.connect(self.appendText)
        self.account_id = "1"
        if config_dict[self.account_id]["state"] is False:
            self.ui.toggle.setStyleSheet("background-color : #d83c3e")
            self.ui.toggle.setText(f"Bot {self.account_id} Disabled")
        else:
            self.ui.toggle.setStyleSheet("background-color : #2d7d46")
            self.ui.toggle.setText(f"Bot {self.account_id} Enabled")
            self.output.emit(
                [f"output_text_{self.account_id}", f"Started Bot {self.account_id}"]
            )
        self.ui.toggle.clicked.connect(lambda: self.check())

        # Sidebar
        sidebar_buttons = ["home", "settings", "commands", "auto_buy"]
        for button in sidebar_buttons:
            getattr(self.ui, f"{button}_btn").clicked.connect(
                lambda checked, button=button: self.sidebar(
                    getattr(self.ui, f"{button}_btn"),
                    getattr(self.ui, f"{button}_widget_{self.account_id}"),
                )
            )

        self.ui.account_btn_1.setStyleSheet("background-color: #5865f2;")
        self.ui.add_account_btn.clicked.connect(self.add_account)
        self.ui.minus_account_btn.clicked.connect(self.delete_account)

    def onUpdateText(self, text):
        for account_id in map(str, range(1, len(config_dict) + 1)):
            getattr(self.ui, f"output_text_{account_id}").setTextColor(
                QColor(216, 60, 62)
            )
            cursor = getattr(self.ui, f"output_text_{account_id}").textCursor()
            cursor.insertText("‎")
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(text)
            getattr(self.ui, f"output_text_{account_id}").setTextCursor(cursor)
            getattr(self.ui, f"output_text_{account_id}").ensureCursorVisible()

    @asyncSlot()
    async def check(self):
        if config_dict[self.account_id]["state"] is False:
            config_dict[self.account_id].update({"state": True})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
            self.ui.toggle.setStyleSheet("background-color : #2d7d46")
            self.ui.toggle.setText(f"Bot {self.account_id} Enabled")
            self.output.emit(
                [f"output_text_{self.account_id}", f"Started Bot {self.account_id}"]
            )
        else:
            config_dict[self.account_id].update({"state": False})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
            self.ui.toggle.setStyleSheet("background-color : #d83c3e")
            self.ui.toggle.setText(f"Bot {self.account_id} Disabled")
            self.output.emit(
                [f"output_text_{self.account_id}", f"Stopped Bot {self.account_id}"]
            )

    @asyncSlot()
    async def sidebar(self, button, widget):
        buttons = [
            self.ui.home_btn,
            self.ui.settings_btn,
            self.ui.commands_btn,
            self.ui.auto_buy_btn,
        ]
        for i in buttons:
            if i == button:
                button.setStyleSheet("background-color: #5865f2")
            else:
                i.setStyleSheet("background-color: #42464d")
        getattr(self.ui, f"main_menu_widget_{self.account_id}").setCurrentWidget(widget)

    @asyncSlot()
    async def accounts(self, account_id):
        for i in range(1, len(config_dict) + 1):
            if i == int(account_id):
                self.account_id = account_id
                getattr(self.ui, f"account_btn_{i}").setStyleSheet(
                    "background-color: #5865f2"
                )
                if config_dict[self.account_id]["state"] is False:
                    self.ui.toggle.setStyleSheet("background-color : #d83c3e")
                    self.ui.toggle.setText(f"Bot {self.account_id} Disabled")
                else:
                    self.ui.toggle.setStyleSheet("background-color : #2d7d46")
                    self.ui.toggle.setText(f"Bot {self.account_id} Enabled")
            else:
                getattr(self.ui, f"account_btn_{i}").setStyleSheet(
                    "background-color: #42464d"
                )
        self.ui.main_menu_widget.setCurrentWidget(
            getattr(self.ui, f"account_widget_{account_id}")
        )
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
            if config_dict[self.account_id]["discord_token"] != "":
                threading.Thread(
                    target=between_callback,
                    args=(
                        config_dict[self.account_id]["discord_token"],
                        self.account_id,
                    ),
                ).start()
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
                    QtGui.QPixmap(":/icons/icons/user.png"),
                    QtGui.QIcon.Mode.Normal,
                    QtGui.QIcon.State.Off,
                )
                getattr(self.ui, f"account_btn_{self.account_id}").setIconSize(
                    QtCore.QSize(22, 22)
                )
                getattr(window.ui, f"account_btn_{self.account_id}").setIcon(icon)
        elif command == "trivia_chance":
            config_dict[self.account_id].update(
                {"trivia_correct_chance": int(state) / 100}
            )
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        else:
            config_dict[self.account_id].update({command: state})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def add_account(self):
        with open("config.json", "r+") as file:
            config_dict = json.load(file)
            account_id = len(config_dict) + 1
            config_dict[account_id] = {
                "state": False,
                "trivia_correct_chance": 0.75,
                "channel_id": "",
                "discord_token": "",
                "offline": False,
                "alerts": False,
                "autobuy": {
                    "lifesavers": {"state": True, "amount": 5},
                    "fishing": False,
                    "shovel": False,
                    "rifle": False,
                },
                "commands": {
                    "trivia": False,
                    "dig": False,
                    "fish": False,
                    "hunt": False,
                    "pm": False,
                    "beg": False,
                    "pet": False,
                    "hl": False,
                    "search": False,
                    "dep_all": False,
                    "stream": False,
                    "work": False,
                    "daily": False,
                    "crime": False,
                },
            }
            file.seek(0)
            json.dump(config_dict, file, ensure_ascii=False, indent=4)
            file.truncate()
        load_account(self, str(account_id))

    @asyncSlot()
    async def delete_account(self):
        with open("config.json", "r+") as file:
            config_dict = json.load(file)
            getattr(self.ui, f"account_btn_{len(config_dict)}").deleteLater()
            config_dict.pop(str(len(config_dict)))
            file.seek(0)
            json.dump(config_dict, file, ensure_ascii=False, indent=4)
            file.truncate()

    def appendText(self, data):
        getattr(self.ui, data[0]).setTextColor(QColor(232, 230, 227))
        cursor = getattr(self.ui, data[0]).textCursor()
        cursor.insertText("‎")
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(data[1] + "\n")
        getattr(self.ui, data[0]).setTextCursor(cursor)
        getattr(self.ui, data[0]).ensureCursorVisible()


def between_callback(token, account_id):
    getattr(window.ui, f"account_btn_{account_id}").setText("Logging In")
    icon = QtGui.QIcon()
    icon.addPixmap(
        QtGui.QPixmap(":/icons/icons/loading.png"),
        QtGui.QIcon.Mode.Normal,
        QtGui.QIcon.State.Off,
    )
    getattr(window.ui, f"account_btn_{account_id}").setIcon(icon)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot(token, account_id))
    loop.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    version = requests.get(
        "https://raw.githubusercontent.com/BridgeSenseDev/Dank-Memer-Grinder/main/"
        "resources/version.txt"
    ).text
    window = MainWindow()
    if int(version.replace(".", "")) > 140:
        updater = UpdaterWindow()
    else:
        window.show()
    for account in map(str, range(1, len(config_dict) + 1)):
        if config_dict[account]["discord_token"] != "":
            threading.Thread(
                target=between_callback,
                args=(config_dict[account]["discord_token"], account),
            ).start()
        else:
            getattr(window.ui, f"account_btn_{account}").setText(f"Account {account}")
            icon = QtGui.QIcon()
            icon.addPixmap(
                QtGui.QPixmap(":/icons/icons/user.png"),
                QtGui.QIcon.Mode.Normal,
                QtGui.QIcon.State.Off,
            )
            getattr(window.ui, f"account_btn_{account}").setIcon(icon)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    loop.run_forever()
    sys.exit(os._exit(0))
