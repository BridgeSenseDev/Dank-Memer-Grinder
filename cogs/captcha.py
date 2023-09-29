import contextlib
import io
import os
import sys

import cv2
import numpy
import numpy as np
import onnxruntime
import requests
from PIL import Image
from discord.ext import commands
from unidecode import unidecode

classes = {
    0: "APlus",
    1: "AdventureBoxOpen",
    2: "AdventureTicket",
    3: "AdventureVoucher",
    4: "AhaPitcherPlant",
    5: "AipheysGemstone",
    6: "Alcohol",
    7: "AlexasMegaphone",
    8: "AlienSample",
    9: "Amathinesbutterfly",
    10: "Ant",
    11: "AntiRobPack",
    12: "Apple",
    13: "ArmpitHair",
    14: "Baby",
    15: "BadoszCard2",
    16: "Baguette",
    17: "BakeggCake",
    18: "BanHammer",
    19: "Banana",
    20: "BeakerOfSusFluid",
    21: "Bean",
    22: "BeanPlayer",
    23: "BeanSeeds",
    24: "BerriesAndCream",
    25: "BirthdayCake",
    26: "BlackHole",
    27: "BluesPlane",
    28: "Boar",
    29: "BoltCutters",
    30: "BottleOfWhiskey",
    31: "BoxceptionClosed",
    32: "BoxxoChoccy",
    33: "Broccoli",
    34: "BroccoliSeeds",
    35: "Bullet",
    36: "BunnysApron",
    37: "Cactus",
    38: "Candy",
    39: "CandyCane",
    40: "CandyCorn",
    41: "Capybara",
    42: "Carrot",
    43: "ChillPill",
    44: "ChristmasPresent",
    45: "ChristmasTree",
    46: "ChristmasTreeDeco",
    47: "CoinBomb",
    48: "CoinVoucher",
    49: "CommonFish",
    50: "Compass",
    51: "Cookie",
    52: "Corn",
    53: "CornBag",
    54: "Coupon",
    55: "CowBoyHat",
    56: "CreditCard",
    57: "CupidToe",
    58: "DailyBoxClosed",
    59: "DankBoxClosed",
    60: "DarkusHoodie",
    61: "Deer",
    62: "DevBoxClosed",
    63: "Diaper",
    64: "DiggingTrophy",
    65: "Duck",
    66: "DuctTape",
    67: "Ectoplasm",
    68: "ElfOnTheShelf",
    69: "EmpoweredFartBottle",
    70: "EnergyDrink",
    71: "ExclusiveWebsiteBoxClosed",
    72: "ExoticFish",
    73: "FakeID",
    74: "FartInABottle",
    75: "FertilizerBag",
    76: "FidgetSpinner",
    77: "FishingBait",
    78: "FishingTrophy",
    79: "FoolsNotif",
    80: "Fossil",
    81: "GenericPetFeces",
    82: "GenericPetFood",
    83: "GiftBox",
    84: "GodBoxClosed",
    85: "GoldenCorndog",
    86: "Grass",
    87: "GraveStone",
    88: "GreenScreen",
    89: "GrindPack",
    90: "Hanukkahcandles",
    91: "Headphones",
    92: "Hoe",
    93: "HolyBread",
    94: "HolyWater",
    95: "HorseSaddle",
    96: "Hotdog",
    97: "HuntingTrophy",
    98: "IronShovel",
    99: "JackyOLanty",
    100: "JarOfSingularity",
    101: "JellyFish",
    102: "Junk",
    103: "KablesSunglasses",
    104: "Karen",
    105: "Keyboard",
    106: "King",
    107: "Kraken",
    108: "Ladybug",
    109: "Landmine",
    110: "Lasso",
    111: "LawDegree",
    112: "LegendaryFish",
    113: "Letter",
    114: "LifeSaver",
    115: "LikeButton",
    116: "LowRifle",
    117: "LuckyHorseshoe",
    118: "MedFishingPole",
    119: "MelmsiesBeard",
    120: "MemeBoxClosed",
    121: "MemePills",
    122: "Meteorite",
    123: "Microphone",
    124: "MoleMan",
    125: "MotivationalPoster",
    126: "Mouse",
    127: "NewPlayerPack",
    128: "NormalPotato",
    129: "NormieBoxClosed",
    130: "Note",
    131: "OddEye",
    132: "OldCowboyRevolver",
    133: "Ornament",
    134: "PatreonBoxClosed",
    135: "PatreonPack",
    136: "PepeBoxClosed",
    137: "PepeCoin",
    138: "PepeCrown",
    139: "PepeMedal",
    140: "PepeRibbon",
    141: "PepeRing",
    142: "PepeStatue",
    143: "PepeSus",
    144: "PepeTrophy",
    145: "PetCollar",
    146: "PinkRubberDucky",
    147: "PinkSludgeMonster",
    148: "Pizza",
    149: "PlasticBag",
    150: "PlasticsBoxClosed",
    151: "PoliceBadge",
    152: "Postcard",
    153: "PotatoCrate",
    154: "PrestigeCoin",
    155: "PrestigePack",
    156: "PuzzleKey",
    157: "RareFish",
    158: "ReversalCard",
    159: "Ring",
    160: "RingLight",
    161: "RobbersMask",
    162: "RobbersWishlist",
    163: "RotsevnisStonkCoin",
    164: "RoyalBoxClosed",
    165: "RustyMachine",
    166: "SantasBag",
    167: "SantasHat",
    168: "ScaryMask",
    169: "Scepter",
    170: "SeaWeed",
    171: "ShootingStar",
    172: "Skunk",
    173: "SludgeBarrel",
    174: "SnowBall",
    175: "SoundCard",
    176: "Spider",
    177: "SpurBoots",
    178: "StackOfCash",
    179: "StarFragment",
    180: "StickBug",
    181: "Stocking",
    182: "StolenAmulet",
    183: "StonksMachine",
    184: "StreakFreeze",
    185: "SugarSkull",
    186: "SunbearD20",
    187: "Taco",
    188: "Tidepod",
    189: "TipJar",
    190: "ToiletPaper",
    191: "TowniesEyes",
    192: "Trash",
    193: "TreasureMap",
    194: "TriviaTrophy",
    195: "TumbleWeed",
    196: "Urinal",
    197: "Vaccine",
    198: "VoodooDoll",
    199: "VotePack",
    200: "WaterBucket",
    201: "WateringCan",
    202: "Watermelon",
    203: "WatermelonSeeds",
    204: "WeddingGift",
    205: "WeetsDonut",
    206: "WiltedFlower",
    207: "WinningLotteryTicket",
    208: "WoodBoxClosed",
    209: "WorkBoxClosed",
    210: "Worm",
    211: "YengsPaw",
    212: "banknote",
    213: "blob",
    214: "caipirinha",
    215: "laptop",
    216: "legacyBunny",
    217: "lotusflower",
    218: "lotusseed",
    219: "padlock",
    220: "partypopper",
    221: "phone",
    222: "rarepepe",
    223: "sand",
    224: "shreddedcheese",
    225: "strawberrycreamshake",
    226: "zombees",
}


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


ort_session = onnxruntime.InferenceSession(
    resource_path("./resources/model.onnx"), providers=["CPUExecutionProvider"]
)


def predict_classes(image_pil):
    image = image_pil.resize((416, 416))
    image = np.array(image).astype(np.float32) / 255.0
    image = np.transpose(image, (2, 0, 1))
    image = np.expand_dims(image, axis=0)

    input_name = ort_session.get_inputs()[
        0
    ].name  # Assuming 'images' is the first input
    output_name = ort_session.get_outputs()[0].name
    input_data = {input_name: image}  # Use the correct input name here
    output = ort_session.run([output_name], input_data)

    return output[0][0]


def download_image(url):
    response = requests.get(url)
    image_data = io.BytesIO(response.content)

    image_pil = Image.open(image_data)
    image_np = cv2.cvtColor(numpy.array(image_pil), cv2.COLOR_RGB2BGR)

    return {"pil": image_pil, "np": image_np}


class Captcha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.bot.state or message.channel.id != self.bot.channel_id:
            return

        with contextlib.suppress(KeyError):
            if not message.embeds:
                return
            embed = message.embeds[0].to_dict()
            embed["title"] = unidecode(embed["title"])

            if "captcha" not in embed["title"].lower():
                return

            # Matching image captcha
            if (
                "click the button with matching image" in embed["description"].lower()
                and f"<@{self.bot.user.id}>" in message.content
            ):
                self.bot.log(f"Matching Image Captcha URL: {message.jump_url}", "red")

                captcha_img = download_image(message.embeds[0].image.url)

                class_probabilities = predict_classes(captcha_img["pil"])
                highest_prob = -1

                for button_idx, button in enumerate(message.components[0].children):
                    emoji_name = button.emoji.name

                    if emoji_name not in list(classes.values()):
                        continue
                    probability = class_probabilities[
                        list(classes.values()).index(emoji_name)
                    ]
                    if probability > highest_prob:
                        highest_prob = probability
                        predicted_emoji_index = button_idx
                        predicted_answer_prob = probability * 100

                self.bot.log(
                    f"Clicked best matching emoji {predicted_emoji_index + 1} with"
                    f" probability {predicted_answer_prob:.2f}%",
                    "green",
                )

                await self.bot.click(message, 0, predicted_emoji_index)


async def setup(bot):
    await bot.add_cog(Captcha(bot))
