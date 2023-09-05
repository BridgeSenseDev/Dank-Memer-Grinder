import asyncio
import contextlib
import ctypes
import io
import json
import os
import platform
import random
import subprocess
import sys
import tempfile
import threading
from collections import OrderedDict

# noinspection PyUnresolvedReferences
import cv2
import discord.errors

# noinspection PyUnresolvedReferences
import onnxruntime
import requests

# noinspection PyUnresolvedReferences
import unidecode
from discord.ext import commands, tasks
from PIL import Image, ImageDraw
from PyQt5.QtCore import pyqtSignal

# noinspection PyUnresolvedReferences
from PyQt5.QtGui import QColor, QFontDatabase, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow
from qasync import QEventLoop, asyncSlot

# noinspection PyUnresolvedReferences
import resources.icons
from resources.interface import *
from resources.load_account import load_account
from resources.updater import *

with contextlib.suppress(AttributeError):
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("dankmemergrinder")

commands_dict = {
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
    "adventure": "adventure",
}

config_example = {
    "state": False,
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
        "trivia": {"state": False, "delay": 5, "trivia_correct_chance": 0.75},
        "dig": {"state": False, "delay": 30},
        "fish": {"state": False, "delay": 30},
        "hunt": {"state": False, "delay": 30},
        "pm": {"state": False, "delay": 20},
        "beg": {"state": False, "delay": 40},
        "pet": {"state": False, "delay": 1800},
        "hl": {"state": False, "delay": 20},
        "search": {
            "state": False,
            "delay": 20,
            "priority": [
                "phoenix pits",
                "aeradella's home",
                "shadow's realm",
                "dog",
                "grass",
                "air",
                "kitchen",
                "dresser",
                "mail box",
                "bed",
                "couch",
                "pocket",
                "toilet",
                "washer",
                "who asked",
            ],
            "second_priority": ["fridge", "twitter", "vacuum"],
            "avoid": [
                "bank",
                "discord",
                "immortals dimension",
                "laundromat",
                "soul's chamber",
                "police officer",
                "tesla",
                "supreme court",
            ],
        },
        "dep_all": {"state": False, "delay": 30},
        "stream": {
            "state": False,
            "delay": 660,
            "order": [1, 1, 1, 1, 1, 0, 0, 0, 2, 2, 2],
        },
        "work": {"state": False, "delay": 3600},
        "daily": {"state": False, "delay": 86400},
        "crime": {
            "state": False,
            "delay": 40,
            "priority": [
                "hacking",
                "tax evasion",
                "fraud",
                "eating a hot dog sideways",
                "trespassing",
            ],
            "second_priority": ["bank robbing", "murder"],
            "avoid": ["arson", "dui", "treason"],
        },
        "adventure": {"state": True, "delay": 1800, "adventure": "west"},
    },
    "autouse": {
        "state": False,
        "hide_disabled": False,
        "pizza_slice": {"state": False},
        "cowboy_boots": {"state": False},
        "lucky_horseshoe": {"state": False},
        "daily_box": {"state": False},
        "apple": {"state": False},
        "ammo": {"state": False},
        "energy_drink": {"state": False},
        "fishing_bait": {"state": False},
        "bank_note": {"state": False},
    },
}

global_config_example = {
    "min_click_delay": 400,
    "max_click_delay": 600,
    "min_commands_delay": 2500,
    "adventure": {
        "space": {
            "A friendly alien approached you slowly. What do you do?": "Attack",
            "A small but wise green alien approaches you.": "Do",
            "Oh my god even in space you cannot escape it": "69",
            "This planet seems to be giving off radioactive chemicals. What do you do?": (
                "Distant Scan"
            ),
            "Whaaaat!? You found a space kitchen! It looks like it is full of shady stuff. What do you do?": (
                "Inspect"
            ),
            "You accidentally bumped into the Webb Telescope. Oh god.": "Flee",
            "You come upon a dark pyramid shaped ship fighting a spherical white ball looking thing. What do you do?": (
                "Embrace Dark"
            ),
            "You encountered someone named Dank Sidious, what do you do?": "Do it",
            'You find a vending machine selling "Moon Pies". What do you do?': "Buy",
            "You flew past a dying star": "Flee",
            "You found a strange looking object. What do you do?": "Ignore",
            "You got abducted by a group of aliens, who are trying to probe you. What do you do?": (
                "Sit Back and Enjoy"
            ),
            "You ran out of fuel! What next?": "Urinate",
            "You see a shooting star!": "Wish",
            "You uh, just came across a pair of Odd Eyes floating around": "Flee",
            "You're picking up a transmission from deep space!": "*<)#%':]|##",
        },
        "west": {
            "A lady next to a broken down wagon is yelling for help.": "Ignore Her",
            "A snake is blocking your path. What do you want to do?": "Wait",
            "A stranger challenges you to a quick draw. What do you want to do?": (
                "Decline"
            ),
            "Someone is getting ambushed by bandits!": "Ignore them",
            "Someone on the trail is lost and asks you for directions.": "Ignore them",
            "You bump into someone near the horse stables. They challenge you to a duel": (
                "Run away"
            ),
            "You come across a saloon with a poker game going on inside. What do you want to do?": (
                "Join"
            ),
            "You entered the saloon to rest from the journey. What do you want to do?": (
                "Play the piano"
            ),
            "You find a dank cellar with an old wooden box": "Ignore it",
            "You find an abandoned mine. What do you want to do?": "Explore",
            "You found a stray horse. What do you want to do?": "Feed",
            "You get on a train and some bandits decide to rob the train. What do you do?": (
                "Don't hurt me!"
            ),
            "You see some bandits about to rob the local towns bank. What do you do?": (
                "Stop them"
            ),
            "You wander towards an old abandoned mine.": "Go in",
            "You're dying of thirst. Where do you want to get water?": "Cactus",
            "You're riding on your horse and you get ambushed. What do you do?": (
                "Run away"
            ),
            "Your horse sees a snake and throws you off. What do you do?": (
                "Find a new horse"
            ),
            "__**WANTED:**__": "Billy Bob Jr.",
        },
        "brazil": {
            "After a long day shopping for souvenirs in a crowded mall, you stop at the food court to grab some food. What do you order?": (
                "McDonald's"
            ),
            "On your way to the beach, you stop at a comer store to buy some drinks and notice a litle caramel-colored dog is sleeping outside. What do you do?": (
                "Pet the Dog"
            ),
            "While enjoying Carnival, you decide to go to the stadium to watch the samba schools perform. Where do you buy your tickets?": (
                "Online"
            ),
            "While traveling in the city, you hear about Snake Island and decide you have to see if it is really as bad as they say. The boat captain will take you there but demands more money if you want to dock. What do you do?": (
                "Stay on the Boat"
            ),
            "While visiting Rio Grande do Sul, you stop at one of the famous Brazilian steakhouses with all the meat you can eat. What do you want?": (
                "Broccoli"
            ),
            "While visiting São Paulo, you find a place to see capybaras. What do you do?": (
                "Pull up"
            ),
            "You can't get enough of the Brazilian beaches, and decide to spend the day exploring a remote one you found. What do you do first?": (
                "Go Swimming"
            ),
            "You can't visit Rio de Janeiro without touring the Christ the Redeemer statue. How do you get there?": (
                "Bus"
            ),
            "You decide to take an MMA class while visiting to learn from the best. Which style do you choose?": (
                "Capoiera"
            ),
            "You stop at a local bakery for some of the Brazilian cheese bread you've heard so much about. What else do you try?": (
                "Nothing"
            ),
            "You take a boat tour in Manaus to go down the Amazon River. At a fork in the path, the guide tells you to the right are piranhas and left anacondas. Which do you choose?": (
                "Piranhas"
            ),
            "You went to schedule a trip into the Amazon to see the animals. What sort of trip do you book?": (
                "Private Tour"
            ),
        },
        "vacation": {
            "A family road trip is a perfect getaway until you end up lost and without cell service. What do you do?": (
                "Keep Driving"
            ),
            "A family vacation can't be complete without a trip to an amusement park. What ride are you dying to try?": (
                "Waterslide"
            ),
            "A friend tells you about a quaint mountain resort, so you decide to spend a few days enjoying the snow. What do you do after you arrive?": (
                "Go Skiing"
            ),
            "Camping has always relaxed you, so you decide to vacation in the wilderness. What sort of camping do you prefer?": (
                "Rent an RV"
            ),
            "During your vacation in Lisbon, the hotel offers you a small pastry for breakfast. What do you do?": (
                "Pass"
            ),
            "Nothing can beat a romantic vacation in Paris. What do you want to do first?": (
                "Louvre"
            ),
            "You can't go on vacation without doing a little sightseeing. What do you want to see?": (
                "Museum"
            ),
            "You decide it's time to visit some famous landmarks in the United States. Which do you visit first?": (
                "Mt. Rushmore"
            ),
            "You decide the beach sounds like a perfect choice for a weekend away. Which beach do you want to visit?": (
                "Daytona Beach, Florida"
            ),
            "You decide to go stargazing in the Chilean desert, but there are only two flights left. Which do you take?": (
                "Night"
            ),
            "You decide to pick up Badosz and spend the weekend at Legoland. What do you look at first?": (
                "Gift Shop"
            ),
            "You find a discounted whale watching tour and decide to give it a go, but the deal is for two. Who do you take with you?": (
                "Kable"
            ),
            "You get a flyer for some discount cruises that sound wonderful. Which destination do you choose?": (
                "Mediterranean"
            ),
            "Your cruise ship docks at a small island for a day of sun and swimming. What do you do?": (
                "Sunbathe"
            ),
            "While vacationing in Rome, you visit the Colosseum and run into a group of people handing out friendship bracelets. What do you do?": (
                "Take a Bracelet"
            ),
        },
    },
}


class UpdaterWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon(resource_path("resources/icon.ico")))
        QFontDatabase.addApplicationFont(resource_path("fonts/Segoe.ttf"))
        self.ui = UiUpdater()
        self.ui.setup_ui(self)
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
                    "https://github.com/BridgeSenseDev/Dank-Memer-Grinder/blob/"
                    "main/updater/Windows-amd64.exe?raw=true",
                    stream=True,
                )
                temp_file = os.path.join(tempfile.gettempdir(), "Windows-amd64.exe")
                with open(temp_file, "wb") as f:
                    f.write(r.content)
                subprocess.Popen(temp_file)
                sys.exit(os._exit(0))
            case "Linux":
                arch = (
                    "Linux-arm64" if platform.machine() == "aarch64" else "Linux-amd64"
                )
            case "Darwin":
                arch = "Darwin-amd64"
        r = requests.get(
            "https://github.com/BridgeSenseDev/Dank-Memer-Grinder/blob/main/"
            f"updater/{arch}?raw=true",
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


def get_config():
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        configs = {"global": global_config_example}
        for i in range(1, 6):
            configs[str(i)] = config_example
        with open("config.json", "w") as config_file:
            json.dump(configs, config_file, indent=4)
            return configs


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


async def start_bot(token, account_id):
    class MyClient(commands.Bot):
        def __init__(self):
            super().__init__(command_prefix="-", self_bot=True)
            config_dict = get_config()
            self.window = window
            self.account_id = account_id
            self.config_dict = config_dict[self.account_id]
            self.config_example = config_example
            self.state = self.config_dict["state"]
            if config_dict[account_id]["channel_id"]:
                self.channel_id = int(config_dict[account_id]["channel_id"])
            else:
                self.channel_id = 0
            self.channel = None
            self.commands_dict = commands_dict
            self.last_ran = {}
            self.global_config_dict = config_dict["global"]
            for command in self.commands_dict:
                self.last_ran[command] = 0

        @tasks.loop(seconds=5)
        async def update(self):
            with open("config.json", "r") as config_file:
                if str(self.account_id) not in json.load(config_file):
                    sys.exit()
                config_file.seek(0)
                self.config_dict = json.load(config_file)[self.account_id]
                self.state = self.config_dict["state"]
                if self.config_dict["channel_id"] != "" and self.config_dict[
                    "channel_id"
                ] != str(self.channel_id):
                    sys.exit()

        async def click(self, message, component, children, delay=None):
            min_delay, max_delay = delay or (
                config_dict["global"]["min_click_delay"],
                config_dict["global"]["max_click_delay"],
            )
            await asyncio.sleep(random.randint(min_delay, max_delay) / 1000)

            retries = 0
            while retries <= 3:
                try:
                    click = (
                        await message.components[component].children[children].click()
                    )
                    if click.successful:
                        return True
                    else:
                        retries += 1
                except (discord.errors.HTTPException, discord.errors.InvalidData):
                    retries += 1

            self.log("Error: Failed to click button after 3 retries", "red")
            return False

        @staticmethod
        async def select(message, component, children, option, delay=None):
            min_delay, max_delay = delay or (
                config_dict["global"]["min_click_delay"],
                config_dict["global"]["max_click_delay"],
            )
            await asyncio.sleep(random.randint(min_delay, max_delay) / 1000)

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
                        return
                except discord.errors.Forbidden:
                    await self.send(command_name, **kwargs)
                except (
                    discord.errors.DiscordServerError,
                    KeyError,
                    discord.errors.InvalidData,
                ):
                    pass

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

        def log(self, text, color=QColor(232, 230, 227)):
            match color:
                case "red":
                    color = QColor(216, 60, 62)
                case "green":
                    color = QColor(38, 254, 0)
                case "yellow":
                    color = QColor(255, 255, 0)
            self.window.output.emit(
                [
                    f"output_text_{account_id}",
                    text,
                    color,
                ]
            )

        async def is_valid_command(self, message, command, sub_command=""):
            if not message.interaction:
                return False

            try:
                if (
                    "[premium](https://www.patreon.com/dankmemerbot) cooldown is"
                    in message.embeds[0].to_dict()["description"]
                ):
                    return False
            except (IndexError, KeyError):
                pass

            return (
                message.channel.id == self.channel_id
                and self.state
                and message.interaction.name
                == f"{commands_dict[command]} {sub_command}".rstrip()
                and self.config_dict["commands"][command]["state"]
                and message.interaction.user == self.user
                and not message.flags.ephemeral
            )

        async def setup_hook(self):
            if not self.channel_id:
                dank_memer_channel = await (
                    await self.fetch_user(270904126974590976)
                ).create_dm()
                self.channel_id = dank_memer_channel.id

            self.channel = await self.fetch_channel(self.channel_id)

            self.update.start()
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

            # Account image
            with tempfile.TemporaryDirectory() as dirpath:
                path = os.path.join(dirpath, f"account_{account_id}")
                await self.user.display_avatar.save(path)

                img = Image.open(path).convert("RGBA")
                height, width = img.size
                mask = Image.new("L", (height, width), 0)
                draw = ImageDraw.Draw(mask)
                draw.pieslice(
                    ((0, 0), (height, width)), 0, 360, fill=255, outline="white"
                )
                alpha = Image.new("L", (height, width), 0)
                alpha.paste(mask, mask)
                final_img = Image.composite(
                    img, Image.new("RGBA", (height, width), (0, 0, 0, 0)), alpha
                )

                img_bytes = io.BytesIO()
                final_img.save(img_bytes, format="PNG")
                with open(f"{path}.png", "wb") as f:
                    f.write(img_bytes.getvalue())

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
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        getattr(window.ui, f"account_btn_{account_id}").setIcon(icon)
        getattr(window.ui, f"account_btn_{account_id}").setIconSize(
            QtCore.QSize(22, 22)
        )
    except (discord.errors.NotFound, ValueError):
        getattr(window.ui, f"account_btn_{account_id}").setText("Invalid Channel")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/icons/icons/warning.png"),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        getattr(window.ui, f"account_btn_{account_id}").setIcon(icon)
        getattr(window.ui, f"account_btn_{account_id}").setIconSize(
            QtCore.QSize(22, 22)
        )


class Stream(QtCore.QObject):
    new_text = QtCore.pyqtSignal(str)

    def write(self, text):
        self.new_text.emit(str(text))


class MainWindow(QMainWindow):
    output = pyqtSignal(list)

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon(resource_path("resources/icon.ico")))
        self.setWindowTitle("Dank Memer Grinder")
        self.setMinimumWidth(868)
        self.setMinimumHeight(540)
        QFontDatabase.addApplicationFont(resource_path("resources/fonts/Segoe.ttf"))
        config_dict = get_config()
        if "global" not in config_dict:
            new_dict = {"global": global_config_example}
            new_dict.update(config_dict)
            with open("config.json", "w") as file:
                json.dump(new_dict, file, ensure_ascii=False, indent=4)
        else:
            for category in global_config_example:
                if category not in config_dict["global"]:
                    config_dict["global"][category] = global_config_example[category]
                else:
                    if category == "adventure":
                        updated_dict = config_dict["global"]["adventure"].copy()
                        for key, value in global_config_example["adventure"].items():
                            if key not in updated_dict:
                                updated_dict[key] = value

                        sorted_keys = sorted(updated_dict.keys())
                        ordered_dict = OrderedDict(
                            (key, updated_dict[key]) for key in sorted_keys
                        )

                        config_dict["global"]["adventure"] = ordered_dict
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        self.ui = UiDankMemerGrinder()
        self.ui.setup_ui(self)

        # Initialize settings
        for account_id in range(1, len(config_dict)):
            if str(account_id) not in config_dict:
                config_dict = get_config()
                config_dict = {
                    k: v
                    for i, (k, v) in enumerate(config_dict.items())
                    if i != account_id - 1
                }
                with open("config.json", "w") as file:
                    json.dump(config_dict, file, ensure_ascii=False, indent=4)
                continue
            load_account(self, str(account_id), config_example)
            self.ui.home_btn.setStyleSheet("background-color: #5865f2;")
        # noinspection PyArgumentList
        sys.stdout = Stream(new_text=self.on_update_text)
        # noinspection PyArgumentList
        sys.stderr = Stream(new_text=self.on_update_text)
        self.output.connect(self.append_text)
        self.account_id = "1"
        if not config_dict[self.account_id]["state"]:
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
        sidebar_buttons = ["home", "settings", "commands", "auto_buy", "auto_use"]
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

    def on_update_text(self, text):
        config_dict = get_config()
        for account_id in map(str, range(1, len(config_dict))):
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
        config_dict = get_config()
        if not config_dict[self.account_id]["state"]:
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
            self.ui.auto_use_btn,
        ]
        for i in buttons:
            if i == button:
                button.setStyleSheet("background-color: #5865f2")
            else:
                i.setStyleSheet("background-color: #42464d")
        getattr(self.ui, f"main_menu_widget_{self.account_id}").setCurrentWidget(widget)

    @asyncSlot()
    async def accounts(self, account_id):
        config_dict = get_config()
        for i in range(1, len(config_dict)):
            if i == int(account_id):
                self.account_id = account_id
                getattr(self.ui, f"account_btn_{i}").setStyleSheet(
                    "background-color: #5865f2"
                )
                if not config_dict[self.account_id]["state"]:
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
            getattr(self.ui, f"{current_widget.objectName().rsplit('_', 2)[0]}_btn"),
            current_widget,
        )

    @asyncSlot()
    async def commands(self, command, state):
        config_dict = get_config()
        config_dict[self.account_id]["commands"][command].update(state)
        with open("config.json", "w") as file:
            json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def toggle_all(self, state):
        config_dict = get_config()
        for command in config_dict[self.account_id]["commands"]:
            if command != "bj":
                getattr(self.ui, f"{command}_checkbox_{self.account_id}").setChecked(
                    state
                )
                config_dict[self.account_id]["commands"][command].update(
                    {"state": state}
                )
                with open("config.json", "w") as file:
                    json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def autobuy(self, item, state, command=None):
        config_dict = get_config()
        if item == "lifesavers":
            config_dict[self.account_id]["autobuy"][item].update({command: state})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        else:
            config_dict[self.account_id]["autobuy"][item] = state
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def autouse(self, item, state, command=None):
        config_dict = get_config()
        if item == "state":
            config_dict[self.account_id]["autouse"]["state"] = state
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)
        elif item == "hide_disabled":
            if config_dict[self.account_id]["autouse"]["hide_disabled"] != state:
                config_dict[self.account_id]["autouse"]["hide_disabled"] = state
                with open("config.json", "w") as file:
                    json.dump(config_dict, file, ensure_ascii=False, indent=4)
            if state:
                for autouse in config_dict[self.account_id]["autouse"]:
                    if autouse in ["state", "hide_disabled"]:
                        continue
                    if not config_dict[self.account_id]["autouse"][autouse]["state"]:
                        getattr(self.ui, f"{autouse}_frame_{self.account_id}").hide()
            else:
                for autouse in config_dict[self.account_id]["autouse"]:
                    if autouse in ["state", "hide_disabled"]:
                        continue
                    getattr(self.ui, f"{autouse}_frame_{self.account_id}").show()
        elif item == "search":
            for autouse in config_dict[self.account_id]["autouse"]:
                if autouse in ["state", "hide_disabled"]:
                    continue
                if state in autouse:
                    getattr(self.ui, f"{autouse}_frame_{self.account_id}").show()
                else:
                    getattr(self.ui, f"{autouse}_frame_{self.account_id}").hide()
        else:
            config_dict[self.account_id]["autouse"][item].update({command: state})
            with open("config.json", "w") as file:
                json.dump(config_dict, file, ensure_ascii=False, indent=4)

    @asyncSlot()
    async def settings(self, command, state):
        config_dict = get_config()
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
                    QIcon.Mode.Normal,
                    QIcon.State.Off,
                )
                getattr(window.ui, f"account_btn_{self.account_id}").setIcon(icon)
                getattr(self.ui, f"account_btn_{self.account_id}").setIconSize(
                    QtCore.QSize(22, 22)
                )
        elif command == "trivia_correct_chance":
            config_dict[self.account_id]["commands"]["trivia"].update(
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
            account_id = len(config_dict)
            config_dict[account_id] = config_example
            file.seek(0)
            json.dump(config_dict, file, ensure_ascii=False, indent=4)
            file.truncate()
        load_account(self, str(account_id), config_example)

    @asyncSlot()
    async def delete_account(self):
        with open("config.json", "r+") as file:
            config_dict = json.load(file)
            if len(config_dict) <= 2:
                return
            getattr(self.ui, f"account_btn_{len(config_dict) - 1}").deleteLater()
            config_dict.pop(str(len(config_dict) - 1))
            file.seek(0)
            json.dump(config_dict, file, ensure_ascii=False, indent=4)
            file.truncate()

    def append_text(self, data):
        if not len(data) >= 3:
            data.append(QColor(232, 230, 227))
        getattr(self.ui, data[0]).setTextColor(data[2])
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
        QIcon.Mode.Normal,
        QIcon.State.Off,
    )
    getattr(window.ui, f"account_btn_{account_id}").setIcon(icon)
    getattr(window.ui, f"account_btn_{account_id}").setIconSize(QtCore.QSize(25, 25))
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot(token, account_id))
    loop.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    response = requests.get("https://api.dankmemer.tools/version")
    if response.status_code == 200:
        version = response.json()["release"]
        if int(version.replace(".", "")) > 152:
            updater = UpdaterWindow()
        else:
            window = MainWindow()
            window.show()
    else:
        window = MainWindow()
        window.show()

    config_dict = get_config()
    for account in map(str, range(1, len(config_dict))):
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
                QIcon.Mode.Normal,
                QIcon.State.Off,
            )
            getattr(window.ui, f"account_btn_{account}").setIcon(icon)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    loop.run_forever()
    sys.exit(os._exit(0))
