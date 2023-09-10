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

from resources.yoloseg import yolo_seg


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


yolo_seg = yolo_seg(
    resource_path("./resources/yoloseg/best.onnx"), conf_thres=0.5, iou_thres=0.3
)
ort_session = onnxruntime.InferenceSession(resource_path("./resources/siamese.onnx"))


def download_image(url):
    response = requests.get(url)
    image_data = io.BytesIO(response.content)

    if url.endswith("captcha.webp"):
        image_pil = Image.open(image_data)
        image_np = cv2.cvtColor(numpy.array(image_pil), cv2.COLOR_RGB2BGR)

        return {"pil": image_pil, "np": image_np}
    elif url[-3:] == "png":
        image_pil = Image.open(image_data).convert("RGBA")
    else:
        image_pil = extract_gif(image_data)
    image_np = cv2.cvtColor(numpy.array(image_pil), cv2.COLOR_RGBA2BGRA)

    return {"pil": image_pil, "np": image_np}


def extract_gif(image_data):
    gif_pil = Image.open(image_data)
    gif_pil.seek(0)

    # Extract the alpha channel
    alpha = gif_pil.convert("RGBA").split()[-1]
    gif_pil.load()
    result = Image.new("RGBA", gif_pil.size)
    result.paste(gif_pil, mask=alpha)

    return result


def crop_images(img_np, boxes, masks):
    img_pil = Image.fromarray(img_np)
    masks = np.any(masks, axis=0)
    masks = masks.astype(int) * 255

    pil_mask = Image.fromarray(masks).convert("L")
    img_pil = img_pil.convert("RGBA")
    pil_mask_resized = pil_mask.resize(img_pil.size, Image.LANCZOS)
    img_pil.putalpha(pil_mask_resized)

    cropped_images = []

    for box in boxes:
        x1, y1, x2, y2 = box
        x1, y1, x2, y2 = map(
            int, (x1.item(), y1.item(), x2.item(), y2.item())
        )  # Convert tensor coordinates to integers
        cropped = img_pil.crop((x1, y1, x2, y2))
        cropped_cv2 = np.array(cropped)
        cropped_images.append(cropped_cv2)

    return cropped_images


def color_similarity(answer_emoji, segmented_emoji):
    mask = (answer_emoji[..., 3] > 0).astype(np.uint8) * 255
    answer_emoji_with_alpha = cv2.merge([answer_emoji[..., 0:3], mask])

    downscaled_answer_emoji = cv2.resize(
        answer_emoji_with_alpha,
        (segmented_emoji.shape[1], segmented_emoji.shape[0]),
        interpolation=cv2.INTER_AREA,
    )

    image1_lab = cv2.cvtColor(downscaled_answer_emoji, cv2.COLOR_BGR2LAB)
    image2_lab = cv2.cvtColor(segmented_emoji, cv2.COLOR_BGR2LAB)

    hist1 = cv2.calcHist(
        [image1_lab], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]
    )
    hist2 = cv2.calcHist(
        [image2_lab], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256]
    )

    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()

    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_INTERSECT)


def transformation(image):
    image = np.array(image)
    image = image.astype(np.float32) / 255.0  # Convert to float and scale values
    image = np.expand_dims(image, axis=0)
    image = np.expand_dims(image, axis=0)

    return image


def resize_image(img_pil):
    return img_pil.resize((100, 100))


def process_segmented_emoji(img_np):
    img_np = cv2.cvtColor(img_np, cv2.COLOR_BGRA2RGBA)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img_np = cv2.filter2D(img_np, -1, kernel)
    img_np = cv2.convertScaleAbs(img_np, alpha=1.5, beta=10)
    img_np[img_np[..., 3] < 128] = [0, 0, 0, 255]
    img_pil = Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_RGBA2GRAY))
    return resize_image(img_pil)


def get_euclidean_distance(input1, input2):
    ort_inputs = {
        ort_session.get_inputs()[0].name: input1,
        ort_session.get_inputs()[1].name: input2,
    }

    output1, output2 = ort_session.run(None, ort_inputs)
    return np.linalg.norm(output1 - output2)


def get_emoji_tensors(message, top_3_indices):
    input_images = [
        (
            resize_image(
                Image.fromarray(download_image(button.emoji.url)["np"]).convert("L")
            ),
            button_idx,
        )
        for button_idx, button in enumerate(message.components[0].children)
        if button_idx in top_3_indices
    ]

    return [(transformation(img), idx) for img, idx in input_images]


def get_dissimilarity_scores(captcha_img, final_boxes, final_masks, input_tensors):
    dissimilarity_scores = []

    for segmented_emoji in crop_images(captcha_img["np"], final_boxes, final_masks)[:3]:
        segmented_dissimilarity_scores = []

        image = process_segmented_emoji(segmented_emoji)
        x0 = transformation(image)

        for x1, idx in input_tensors:
            euclidean_distance = get_euclidean_distance(x0, x1)

            # Store both euclidean_distance and idx
            segmented_dissimilarity_scores.append((euclidean_distance.item(), idx))

        dissimilarity_scores.append(segmented_dissimilarity_scores)

    return np.array(dissimilarity_scores)


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
                self.bot.log("Matching Image Captcha", "red")

                captcha_img = download_image(message.embeds[0].image.url)
                final_boxes, final_masks = yolo_seg(captcha_img["np"])

                # Get the indices of the top three elements in descending order
                color_similarities = [0] * 5

                for button_idx, button in enumerate(message.components[0].children):
                    emoji_img = download_image(button.emoji.url)

                    for segmented_emoji in crop_images(
                        captcha_img["np"], final_boxes, final_masks
                    )[:3]:
                        similarities = color_similarity(
                            emoji_img["np"], segmented_emoji
                        )
                        color_similarities[button_idx] += similarities

                top_3_indices = sorted(
                    range(len(color_similarities)),
                    key=lambda i: color_similarities[i],
                    reverse=True,
                )[:3]

                emoji_tensors = get_emoji_tensors(message, top_3_indices)
                dissimilarity_scores = get_dissimilarity_scores(
                    captcha_img, final_boxes, final_masks, emoji_tensors
                )

                average_dissimilarity_scores = np.mean(dissimilarity_scores, axis=0)
                min_score_idx = int(
                    average_dissimilarity_scores[
                        np.argmin(average_dissimilarity_scores[:, 0]), 1
                    ]
                )

                self.bot.log(
                    f"Clicked best matching emoji {min_score_idx + 1} with"
                    f" similarity {average_dissimilarity_scores[min_score_idx, 0]}",
                    "green",
                )

                await self.bot.click(message, 0, min_score_idx)


async def setup(bot):
    await bot.add_cog(Captcha(bot))
