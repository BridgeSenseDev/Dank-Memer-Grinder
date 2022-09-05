import asyncio
import ctypes
import sys
import json
import threading

from PyQt6.QtGui import QIcon, QFontDatabase
from PyQt6.QtWidgets import QApplication, QMainWindow
from discord.ext import commands, tasks
from qasync import QEventLoop, asyncSlot

# noinspection PyUnresolvedReferences
import icons
from interface import *

try:
    myappid = 'dankmemergrinder'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass


def update():
    global config_dict
    threading.Timer(10, update).start()
    with open("config.json", "r") as config_file:
        config_dict = json.load(config_file)


update()


class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='-', self_bot=True)
        self.channel = None
        self.channel_id = None
        self.window = None

    async def on_ready(self):
        window.ui.output.append(f"Logged in as {self.user}")
        self.channel_id = config_dict["channel_id"]
        self.channel = self.get_channel(self.channel_id)
        self.window = window
        await self.load_extension("cogs.trivia")
        await self.load_extension("cogs.commands")
        await self.load_extension("cogs.pm")
        await self.load_extension("cogs.hl")
        await self.load_extension("cogs.search")
        await self.load_extension("cogs.stream")
        await self.load_extension("cogs.minigames")
        await self.load_extension("cogs.blackjack")
        await self.load_extension("cogs.autobuy")


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon("icon.png"))
        QFontDatabase.addApplicationFont("Segoe.ttf")
        self.ui = Ui_DankMemerGrinder()
        self.ui.setupUi(self)
        self.bot = MyClient()
        self.show()
        self.ui.output.setVerticalScrollBar(self.ui.output_scrollbar)
        config_dict.update({"state": False})
        with open("config.json", "w") as file:
            json.dump(config_dict, file, ensure_ascii=False, indent=4)

        # Initialize buttons and settings
        for i in config_dict["commands"]:
            try:
                getattr(self.ui, i).setChecked(config_dict["commands"][i])
            except:
                pass
        self.ui.blackjack_btn.setChecked(config_dict["commands"]["bj"]["state"])
        self.ui.multi.setText(str(config_dict["commands"]["bj"]["multi"]))
        self.ui.bj_amount.setText(str(config_dict["commands"]["bj"]["bj_amount"]))

        for i in config_dict["autobuy"]:
            try:
                getattr(self.ui, i).setChecked(config_dict["autobuy"][i])
            except:
                pass
        self.ui.lifesavers.setChecked(config_dict["autobuy"]["lifesavers"]["state"])
        self.ui.lifesavers_amount.setValue(config_dict["autobuy"]["lifesavers"]["amount"])

        self.ui.token.setText(config_dict["discord_token"])
        self.ui.channel.setText(str(config_dict["channel_id"]))
        self.ui.trivia_chance.setValue(int(config_dict["trivia_correct_chance"] * 100))

        # Sidebar buttons
        self.ui.home_btn.clicked.connect(lambda: self.sidebar(self.ui.home_btn, self.ui.home))
        self.ui.settings_btn.clicked.connect(lambda: self.sidebar(self.ui.settings_btn, self.ui.settings))
        self.ui.commands_btn.clicked.connect(lambda: self.sidebar(self.ui.commands_btn, self.ui.commands))
        self.ui.auto_buy_btn.clicked.connect(lambda: self.sidebar(self.ui.auto_buy_btn, self.ui.auto_buy))
        self.ui.gambling_btn.clicked.connect(lambda: self.sidebar(self.ui.gambling_btn, self.ui.gambling))
        self.ui.toggle.clicked.connect(lambda: self.check())

        # Command buttons
        self.ui.trivia.clicked.connect(lambda: self.toggle_command("trivia", self.ui.trivia.isChecked()))
        self.ui.dig.clicked.connect(lambda: self.toggle_command("dig", self.ui.dig.isChecked()))
        self.ui.fish.clicked.connect(lambda: self.toggle_command("fish", self.ui.fish.isChecked()))
        self.ui.hunt.clicked.connect(lambda: self.toggle_command("hunt", self.ui.hunt.isChecked()))
        self.ui.pm.clicked.connect(lambda: self.toggle_command("pm", self.ui.pm.isChecked()))
        self.ui.beg.clicked.connect(lambda: self.toggle_command("beg", self.ui.beg.isChecked()))
        self.ui.hl.clicked.connect(lambda: self.toggle_command("hl", self.ui.hl.isChecked()))
        self.ui.search.clicked.connect(lambda: self.toggle_command("search", self.ui.search.isChecked()))
        self.ui.dep_all.clicked.connect(lambda: self.toggle_command("dep_all", self.ui.dep_all.isChecked()))
        self.ui.stream.clicked.connect(lambda: self.toggle_command("stream", self.ui.stream.isChecked()))
        self.ui.work.clicked.connect(lambda: self.toggle_command("work", self.ui.work.isChecked()))
        self.ui.use_pizza.clicked.connect(lambda: self.toggle_command("use_pizza", self.ui.use_pizza.isChecked()))
        self.ui.start.clicked.connect(lambda: self.toggle_all(True))
        self.ui.stop.clicked.connect(lambda: self.toggle_all(False))

        # Blackjack buttons
        self.ui.blackjack_btn.clicked.connect(lambda: self.blackjack("state", self.ui.blackjack_btn.isChecked()))
        self.ui.multi.textChanged.connect(lambda: self.blackjack("multi", self.ui.multi.text()))
        self.ui.bj_amount.textChanged.connect(lambda: self.blackjack("bj_amount", self.ui.bj_amount.text()))

        # Autobuy buttons
        self.ui.lifesavers.clicked.connect(lambda: self.autobuy("lifesavers", self.ui.lifesavers.isChecked(), "state"))
        self.ui.lifesavers_amount.valueChanged.connect(
            lambda: self.autobuy("lifesavers", self.ui.lifesavers_amount.value(), "amount"))
        self.ui.fishing.clicked.connect(lambda: self.autobuy("fishing", self.ui.fishing.isChecked()))
        self.ui.shovel.clicked.connect(lambda: self.autobuy("shovel", self.ui.shovel.isChecked()))
        self.ui.rifle.clicked.connect(lambda: self.autobuy("rifle", self.ui.rifle.isChecked()))

        # Settings buttons
        self.ui.token.textChanged.connect(lambda: self.settings("token", self.ui.token.text()))
        self.ui.channel.textChanged.connect(lambda: self.settings("channel", self.ui.channel.text()))
        self.ui.trivia_chance.valueChanged.connect(
            lambda: self.settings("trivia_chance", self.ui.trivia_chance.value()))

    @asyncSlot()
    async def check(self):
        if config_dict["state"] is False:
            config_dict.update({"state": True})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
            self.ui.toggle.setStyleSheet("background-color : #2d7d46")
            self.ui.toggle.setText("Bot On")
            self.ui.output.append("Started bot")
            if self.bot.user is None:
                await self.bot.start(config_dict["discord_token"])
        else:
            config_dict.update({"state": False})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
            self.ui.toggle.setStyleSheet("background-color : #d83c3e")
            self.ui.toggle.setText("Bot Off")
            self.ui.output.append("Stopped bot")

    @asyncSlot()
    async def sidebar(self, button, widget):
        buttons = [self.ui.home_btn, self.ui.settings_btn, self.ui.commands_btn, self.ui.auto_buy_btn,
                   self.ui.gambling_btn]
        for i in buttons:
            if i == button:
                button.setStyleSheet("background-color: #5865f2")
            else:
                i.setStyleSheet("background-color: #42464d")
        self.ui.stackedWidget.setCurrentWidget(widget)

    @asyncSlot()
    async def toggle_command(self, command, state):
        config_dict["commands"].update({command: state})
        with open("config.json", "w") as file:
            json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def toggle_all(self, state):
        for i in config_dict["commands"]:
            if i != "bj":
                getattr(self.ui, i).setChecked(state)
                config_dict["commands"].update({i: state})
                with open("config.json", "w") as file:
                    json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def blackjack(self, command, state):
        config_dict["commands"]["bj"].update({command: state})
        with open("config.json", "w") as file:
            json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def autobuy(self, item, state, command=None):
        if item == "lifesavers":
            config_dict["autobuy"][item].update({command: state})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        else:
            config_dict["autobuy"][item] = state
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def settings(self, command, state):
        if command == "channel":
            config_dict.update({"channel_id": int(state)})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        elif command == "token":
            config_dict.update({"discord_token": state})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        elif command == "trivia_chance":
            config_dict.update({"trivia_correct_chance": int(state) / 100})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    loop.run_forever()
