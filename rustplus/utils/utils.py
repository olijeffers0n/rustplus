import logging
import string
from importlib import resources
from typing import Tuple, Dict

import requests
from PIL import ImageFont, Image, ImageDraw

ICONS_PATH = "rustplus.icons"
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


def convert_event_type_to_name(event: int) -> str:
    if event == 1:
        return "Player"
    elif event == 2:
        return "Explosion"
    elif event == 3:
        return "Vending Machine"
    elif event == 4:
        return "CH47 Chinook"
    elif event == 5:
        return "Cargo Ship"
    elif event == 6:
        return "Locked Crate"
    elif event == 7:
        return "Generic Radius"
    elif event == 8:
        return "Patrol Helicopter"


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


def convert_marker(name, angle) -> Image.Image:
    name_to_file = {
        "2": "explosion.png",
        "4": "chinook.png",
        "5": "cargo.png",
        "6": "crate.png",
        "8": "patrol.png",
    }

    with resources.path(ICONS_PATH, name_to_file[name]) as path:
        icon = Image.open(path).convert("RGBA")

    if name == "6":
        icon = icon.resize((85, 85))
    elif name == "2":
        icon = icon.resize((96, 96))
    elif name in ["4", "8"]:
        blades_file = "chinook_blades.png"
        blades_size = (100, 100) if name == "4" else (200, 200)

        with resources.path(ICONS_PATH, blades_file) as path:
            blades = Image.open(path).convert("RGBA")
        blades = blades.resize(blades_size)

        if name == "4":
            icon.paste(blades, (64 - 50, 96 - 50), blades)
            icon.paste(blades, (64 - 50, 32 - 50), blades)
        else:
            icon = icon.resize((200, 200))
            icon.paste(blades, (0, 0), blades)

    icon = icon.rotate(angle)
    return icon


def convert_monument(name: str, override_images: Dict[str, Image.Image]) -> Image.Image:
    name_to_file = {
        "supermarket": "supermarket.png",
        "mining_outpost_display_name": "mining_outpost.png",
        "gas_station": "oxums.png",
        "fishing_village_display_name": "fishing.png",
        "large_fishing_village_display_name": "fishing.png",
        "lighthouse_display_name": "lighthouse.png",
        "excavator": "excavator.png",
        "water_treatment_plant_display_name": "water_treatment.png",
        "train_yard_display_name": "train_yard.png",
        "outpost": "outpost.png",
        "bandit_camp": "bandit.png",
        "junkyard_display_name": "junkyard.png",
        "dome_monument_name": "dome.png",
        "satellite_dish_display_name": "satellite.png",
        "power_plant_display_name": "power_plant.png",
        "military_tunnels_display_name": "military_tunnels.png",
        "airfield_display_name": "airfield.png",
        "launchsite": "launchsite.png",
        "sewer_display_name": "sewer.png",
        "oil_rig_small": "small_oil_rig.png",
        "large_oil_rig": "large_oil_rig.png",
        "underwater_lab": "underwater_lab.png",
        "AbandonedMilitaryBase": "desert_base.png",
        "ferryterminal": "ferryterminal.png",
        "harbor_display_name": "harbour.png",
        "harbor_2_display_name": "harbour.png",
        "arctic_base_a": "arctic_base.png",
        "arctic_base_b": "arctic_base.png",
        "missile_silo_monument": "missile_silo.png",
        "stables_a": "stables.png",
        "stables_b": "stables.png",
        "mining_quarry_stone_display_name": "mining_quarry_stone.png",
        "mining_quarry_sulfur_display_name": "mining_quarry_sulfur.png",
        "mining_quarry_hqm_display_name": "mining_quarry_hqm.png",
        "train_tunnel_link_display_name": "train.png",
        "train_tunnel_display_name": "train.png",
    }

    try:
        return override_images[name]
    except KeyError:
        pass

    if name in name_to_file:
        file_name = name_to_file[name]
        with resources.path(ICONS_PATH, file_name) as path:
            icon = Image.open(path).convert("RGBA")
    elif "swamp" in name:
        with resources.path(ICONS_PATH, "swamp.png") as path:
            icon = Image.open(path).convert("RGBA")
    else:
        logging.getLogger("rustplus.py").info(
            f"{name} - Has no icon, report this as an issue"
        )
        with resources.path(ICONS_PATH, "icon.png") as path:
            icon = Image.open(path).convert("RGBA")

    return icon
