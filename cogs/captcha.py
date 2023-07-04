import io
import json
import os
import sys

import cv2
import numpy as np
import requests
from PIL import Image
from PyQt5.QtGui import QColor
from discord.ext import commands
from unidecode import unidecode

from resources.yoloseg import yolo_seg


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


yolo_seg = yolo_seg(
    resource_path("./resources/yoloseg/best.onnx"), conf_thres=0.5, iou_thres=0.3
)


def similarity(answer_emoji, captcha_emoji):
    answer_emoji_with_alpha = cv2.cvtColor(answer_emoji, cv2.COLOR_BGR2BGRA)
    mask = (answer_emoji_with_alpha[..., 3] > 0).astype(np.uint8) * 255
    answer_emoji_with_alpha = cv2.merge([answer_emoji_with_alpha[..., 0:3], mask])

    downscaled_answer_emoji = cv2.resize(
        answer_emoji_with_alpha,
        (captcha_emoji.shape[1], captcha_emoji.shape[0]),
        interpolation=cv2.INTER_AREA,
    )

    image1_lab = cv2.cvtColor(downscaled_answer_emoji, cv2.COLOR_BGR2LAB)
    image2_lab = cv2.cvtColor(captcha_emoji, cv2.COLOR_BGR2LAB)

    hist1 = cv2.calcHist(
        [image1_lab], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]
    )
    hist2 = cv2.calcHist(
        [image2_lab], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]
    )

    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()

    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_INTERSECT)


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def crop_images(img_np, boxes, masks):
    img_pil = Image.fromarray(img_np)
    masks = np.any(masks, axis=0)
    masks = masks.astype(int) * 255

    pil_mask = Image.fromarray(masks).convert("L")
    img_pil = img_pil.convert("RGBA")
    pil_mask_resized = pil_mask.resize(img_pil.size, Image.LANCZOS)
    img_pil.putalpha(pil_mask_resized)

    cropped_images = []

    for idx, box in enumerate(boxes):
        x1, y1, x2, y2 = box
        x1, y1, x2, y2 = map(
            int, (x1.item(), y1.item(), x2.item(), y2.item())
        )  # Convert tensor coordinates to integers
        cropped = img_pil.crop((x1, y1, x2, y2))
        cropped_cv2 = np.array(cropped)
        cropped_images.append(cropped_cv2)

    return cropped_images


class Captcha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.bot.state:
            return

        try:
            embed = message.embeds[0].to_dict()
            embed["title"] = unidecode(embed["title"])

            if "we're under maintenance!" in embed["title"].lower():
                with open("config.json", "r+") as config_file:
                    config_dict = json.load(config_file)
                    for account_id in (str(i) for i in range(1, len(config_dict))):
                        config_dict[account_id]["state"] = False
                        self.bot.window.output.emit(
                            [
                                f"output_text_{account_id}",
                                (
                                    "All bots have been disabled because of a dank"
                                    " memer maintenance\nPlease check if the update is"
                                    " safe before continuing to grind"
                                ),
                                QColor(216, 60, 62),
                            ]
                        )
                    config_file.seek(0)
                    json.dump(config_dict, config_file, indent=4)
                    config_file.truncate()

                self.bot.window.ui.toggle.setStyleSheet("background-color : #d83c3e")
                account = self.bot.window.ui.accounts.currentText()
                self.bot.window.ui.toggle.setText(
                    " ".join(account.split()[:-1] + ["Disabled"])
                )
                return

            if "captcha" not in unidecode(embed["title"]).lower():
                return

            # Matching image captcha
            if (
                "**click the button with matching image.**\nfailing the captcha might"
                " result in a temporary ban."
                in embed["description"].lower()
                and f"<@{self.bot.user.id}>" in message.content
            ):
                self.bot.log(
                    f"Matching Image Captcha",
                    "red",
                )

                response = requests.get(embed["image"]["url"], stream=True).raw
                img_data = np.asarray(bytearray(response.read()), dtype="uint8")
                img_np = cv2.imdecode(img_data, cv2.IMREAD_COLOR)

                final_boxes, final_masks = yolo_seg(img_np)
                segmented_emojis = crop_images(img_np, final_boxes, final_masks)

                color_similarity = [0] * 5

                for button_idx, button in enumerate(message.components[0].children):
                    emoji = button.emoji.url
                    response = requests.get(emoji)
                    emoji_data = io.BytesIO(response.content)

                    if emoji[-3:] == "png":
                        emoji_pil = Image.open(emoji_data)
                    elif emoji[-3:] == "gif":
                        gif_pil = Image.open(emoji_data)
                        gif_pil.seek(0)
                        alpha = gif_pil.convert("RGBA").split()[
                            -1
                        ]  # extract the alpha channel
                        gif_pil.load()  # make sure PIL has loaded the file
                        emoji_pil = Image.new("RGBA", gif_pil.size)
                        emoji_pil.paste(
                            gif_pil, mask=alpha
                        )  # paste the gif using alpha mask

                    emoji_np = np.asarray(emoji_pil)
                    emoji_bgr = cv2.cvtColor(emoji_np, cv2.COLOR_RGB2BGR)

                    for segmented_emoji in segmented_emojis:
                        similarities = similarity(emoji_bgr, segmented_emoji)
                        color_similarity[button_idx] += similarities

                best_match_index = color_similarity.index(max(color_similarity))
                await self.bot.click(message, 0, best_match_index)

                self.bot.log(
                    (
                        f"Clicked best matching emoji {best_match_index + 1} with"
                        f" similarity {color_similarity[best_match_index]}"
                    ),
                    "green",
                )

            # Pepe captcha
            if (
                "**click all buttons with a pepe (green frog) in it.**\nfailing the"
                " captcha might result in a temporary ban."
                in embed["description"].lower()
            ):
                self.bot.log(
                    f"Pepe Captcha",
                    "red",
                )
                for row, i in enumerate(message.components):
                    for column, button in enumerate(i.children):
                        if not button.emoji:
                            await self.bot.click(message, row, column)
                            await self.bot.click(message, row, column)
                            self.bot.log(
                                f"Pepe Captcha Solved",
                                "red",
                            )
                            return
                        if button.emoji.id in [
                            819014822867894304,
                            796765883120353280,
                            860602697942040596,
                            860602923665588284,
                            860603013063507998,
                            936007340736536626,
                            933194488241864704,
                            680105017532743700,
                        ]:
                            await self.bot.click(message, row, column)
                            continue

            # Reverse images captcha
            if "pick any of the three wrong images" in embed["description"].lower():
                self.bot.log(
                    f"Wrong Images Captcha",
                    "red",
                )
                captcha_url = embed["image"]["url"]
                for count, button in enumerate(message.components[0].children):
                    if button.emoji.url not in captcha_url:
                        await self.bot.click(message, 0, count)
                self.bot.log(
                    f"Wrong Images Captcha Solved",
                    "green",
                )
                return

            # Reverse pepe captcha
            if (
                "click all buttons without a pepe in them!"
                in embed["description"].lower()
            ):
                self.bot.log(
                    f"Reverse Pepe Captcha",
                    "red",
                )
                for row, i in enumerate(message.components):
                    for column, button in enumerate(i.children):
                        if not button.emoji:
                            await self.bot.click(message, row, column)
                            await self.bot.click(message, row, column)
                            self.bot.log(
                                f"Pepe Captcha Solved",
                                "red",
                            )
                            return
                        if button.emoji.id not in [
                            819014822867894304,
                            796765883120353280,
                            860602697942040596,
                            860602923665588284,
                            860603013063507998,
                            936007340736536626,
                            933194488241864704,
                            680105017532743700,
                        ]:
                            await self.bot.click(message, row, column)
                            continue
        except KeyError:
            pass


async def setup(bot):
    await bot.add_cog(Captcha(bot))
