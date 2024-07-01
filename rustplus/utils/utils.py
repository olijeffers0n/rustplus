import string
from importlib import resources
from typing import Tuple

import requests
from PIL import ImageFont, Image, ImageDraw

ICONS_PATH = "rustplus.api.icons"
FONT_PATH = "rustplus.utils.fonts"
GRID_DIAMETER = 146.28571428571428
PLAYER_MARKER_ONLINE_COLOR = (201, 242, 155, 255)
PLAYER_MARKER_OFFLINE_COLOR = (128, 128, 128, 255)


def convert_time(time) -> str:
    hours, minutes = divmod(time * 60, 60)

    return (
        f"{int(hours)}:0{int(minutes)}"
        if minutes <= 9
        else f"{int(hours)}:{int(minutes)}"
    )


def generate_grid(
    map_size: int,
    text_size: int = 20,
    text_padding: int = 5,
    color: str = "black",
) -> Image.Image:
    img = Image.new("RGBA", (map_size, map_size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    with resources.path(FONT_PATH, "PermanentMarker.ttf") as path:
        font = ImageFont.truetype(str(path), text_size)

    letters = list(string.ascii_uppercase)
    letters.extend(
        a + b for a in string.ascii_uppercase for b in string.ascii_uppercase
    )

    num_cells = int(map_size / GRID_DIAMETER)

    for i in range(num_cells):
        for j in range(num_cells):
            start = (i * GRID_DIAMETER, j * GRID_DIAMETER)
            end = ((i + 1) * GRID_DIAMETER, (j + 1) * GRID_DIAMETER)
            d.rectangle((start, end), outline=color)

            text = letters[i] + str(j)
            text_pos = (start[0] + text_padding, start[1] + text_padding)
            d.text(text_pos, text, fill=color, font=font)

    return img


def format_coord(x: int, y: int, map_size: int) -> Tuple[int, int]:
    # Adjust y and x coordinates with offsets
    y = max(0, min(map_size - y - 75, map_size - 150))
    x = max(0, min(x - 75, map_size - 150))

    return x, y


async def fetch_avatar_icon(steam_id: int, online: bool) -> Image.Image:
    avatar = (
        Image.open(
            requests.get(
                f"https://companion-rust.facepunch.com/api/avatar/{steam_id}",
                stream=True,
            ).raw
        )
        .resize((100, 100), Image.LANCZOS)
        .convert("RGBA")
    )

    return await avatar_processing(avatar, 5, online)


async def avatar_processing(
    image: Image.Image, border_size: int, player_online: bool = False
) -> Image.Image:
    size_with_border = (
        image.size[0] + 2 * border_size,
        image.size[1] + 2 * border_size,
    )

    border_image = Image.new("RGBA", size_with_border, (0, 0, 0, 0))

    mask = Image.new("L", size_with_border, 0)
    draw = ImageDraw.Draw(mask)

    draw.ellipse([0, 0, size_with_border[0], size_with_border[1]], fill=255)

    border_layer = Image.new(
        "RGBA",
        size_with_border,
        PLAYER_MARKER_ONLINE_COLOR if player_online else PLAYER_MARKER_OFFLINE_COLOR,
    )
    border_image.paste(border_layer, mask=mask)

    image_mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(image_mask)
    draw.ellipse([0, 0, image.size[0], image.size[1]], fill=255)

    border_image.paste(image, (border_size, border_size), image_mask)

    return border_image
