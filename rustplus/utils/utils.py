import logging
import string
from importlib import resources
from typing import Tuple

import requests
from PIL import ImageFont, Image, ImageDraw
from pathlib import Path
from resvg import render, usvg
from io import BytesIO

ICONS_PATH = "rustplus.icons"
FONT_PATH = "rustplus.utils.fonts"
GRID_DIAMETER = 146.28571428571428
PLAYER_MARKER_ONLINE_COLOR = (201, 242, 155, 255)
PLAYER_MARKER_OFFLINE_COLOR = (128, 128, 128, 255)


def error_present(app_message) -> bool:
    """
    Checks message for error
    """
    return app_message.response.error.error != ""


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


def convert_coordinates(coords: Tuple[int, int], map_size: int) -> Tuple[str, int]:
    grids = list(string.ascii_uppercase)
    grids.extend(a + b for a in string.ascii_uppercase for b in string.ascii_uppercase)

    return grids[int(coords[0] // GRID_DIAMETER)], int(
        (map_size - coords[1]) // GRID_DIAMETER
    )


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


def convert_marker(marker_type: int, angle) -> Image.Image:
    name_to_file = {
        2: "explosion.png",
        4: "chinook.png",
        5: "cargo.png",
        6: "crate.png",
        8: "patrol.png",
    }

    with resources.path(ICONS_PATH, name_to_file[marker_type]) as path:
        icon = Image.open(path).convert("RGBA")

    if marker_type == 6:
        icon = icon.resize((85, 85))
    elif marker_type == 2:
        icon = icon.resize((96, 96))
    elif marker_type == 4 or marker_type == 8:
        blades_file = "chinook_blades.png"
        blades_size = (100, 100) if marker_type == 4 else (200, 200)

        with resources.path(ICONS_PATH, blades_file) as path:
            blades = Image.open(path).convert("RGBA")
        blades = blades.resize(blades_size)

        if marker_type == 4:
            icon.paste(blades, (64 - 50, 96 - 50), blades)
            icon.paste(blades, (64 - 50, 32 - 50), blades)
        else:
            icon = icon.resize((200, 200))
            icon.paste(blades, (0, 0), blades)

    icon = icon.rotate(angle)
    return icon


def convert_monument_to_image(name: str) -> Image.Image:
    name_to_file = {
        "ferryterminal": "Ferry_Terminal.svg",
        "train_tunnel_display_name": "Tunnel_Entrance.svg",
        "train_tunnel_link_display_name": "Tunnel_Entrance.svg",
        "apartmentcomplex": "Apartments_Complex.svg",
        "harbor_display_name": "Harbor.svg",
        "harbor_2_display_name": "Harbor.svg",
        "large_fishing_village_display_name": "Fishing_Village.svg",
        "fishing_village_display_name": "Fishing_Village.svg",
        "AbandonedMilitaryBase": "Military_Base.svg",
        "power_plant_display_name": "Powerplant.svg",
        "missile_silo_monument": "Missile_Silo.svg",
        "outpost": "Outpost.svg",
        "bandit_camp": "Bandit_Camp.svg",
        "stables_a": "Stables.svg",
        "stables_b": "Stables.svg",
        "mining_quarry_stone_display_name": "Stone_Quarry.svg",
        "mining_quarry_sulfur_display_name": "Sulfur_Quarry.svg",
        "mining_quarry_hqm_display_name": "HQM_Quarry.svg",
        "satellite_dish_display_name": "Satellite_Dish.svg",
        "dome_monument_name": "Dome.svg",
        "junkyard_display_name": "Junkyard.svg",
        "sewer_display_name": "Sewer_Branch.svg",
        "oil_rig_small": "Oil_Rig_Small.svg",
        "large_oil_rig": "Oil_Rig_Large.svg",
        "lighthouse_display_name": "Lighthouse.svg",
        "mining_outpost_display_name": "Mining_Outpost.svg",
        "supermarket": "Supermarket.svg",
        "arctic_base_a": "Arctic_Research_Base.svg",
        "arctic_base_b": "Arctic_Research_Base.svg",
        "launchsite": "Launch_Site.svg",
        "water_treatment_plant_display_name": "Water_Treatment.svg",
        "excavator": "Excavator.svg",
        "train_yard_display_name": "Trainyard.svg",
        "airfield_display_name": "Airfield.svg",
        "military_tunnels_display_name": "Military_Tunnels.svg",
        "gas_station": "Gas_Station.svg",
        "jungle_ziggurat": "Jungle_Ziggurat.svg",
        "radtown": "Radtown.svg",
    }

    if name in name_to_file:
        file_name = name_to_file[name]
        with resources.path(ICONS_PATH, file_name) as path:
            if file_name.endswith(".png"):
                return Image.open(path).convert("RGBA")
            elif file_name.endswith(".svg"):
                return svg_to_pil(path, (150, 150))
            else:
                logging.getLogger("rustplus.py").info(
                    f"{name} - Has no icon, report this as an issue"
                )
                with resources.path(ICONS_PATH, "icon.png") as path:
                    return Image.open(path).convert("RGBA")

    elif "swamp" in name:
        with resources.path(ICONS_PATH, "Swamp.svg") as path:
            return svg_to_pil(path, (150, 150))
    elif "underwater_lab" in name:
        # Same story with swamp, no rust+ specific token so prefab name is sent instead
        with resources.path(ICONS_PATH, "Underwater_Lab.svg") as path:
            return svg_to_pil(path, (150, 150))
    else:
        logging.getLogger("rustplus.py").info(
            f"{name} - Has no icon, report this as an issue"
        )
        with resources.path(ICONS_PATH, "icon.png") as path:
            icon = Image.open(path).convert("RGBA")

    return icon


def svg_to_pil(filepath: str | Path, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size

    svg = Path(filepath).read_text()

    opts = usvg.Options.default()
    tree = usvg.Tree.from_str(svg, opts)

    orig_w, orig_h = tree.int_size()

    # Preserve aspect ratio (fit inside target)
    scale_x = target_w / orig_w
    scale_y = target_h / orig_h
    scale = min(scale_x, scale_y)  # use max for "cover" behavior

    # center the scaled image in the target canvas
    tx = (target_w - orig_w * scale) / 2.0
    ty = (target_h - orig_h * scale) / 2.0

    # transform tuple format: (a, b, c, d, e, f)
    # corresponds to the affine matrix rows:
    # [ a  b  c ]
    # [ d  e  f ]
    transform_fit = (scale, 0.0, tx, 0.0, scale, ty)

    png_bytes = render(
        tree,
        transform_fit,
        bg_size=(target_w, target_h),
    )

    return Image.open(BytesIO(png_bytes)).convert("RGBA")
