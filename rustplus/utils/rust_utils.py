from importlib import resources
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
import logging
import string

from ..api.remote.rustplus_proto import AppMessage
from ..api.structures import RustTime

ICONS_PATH = "rustplus.api.icons"
FONT_PATH = "rustplus.utils.fonts"
GRID_DIAMETER = 146.28571428571428

PLAYER_MARKER_ONLINE_COLOR = (201, 242, 155, 255)
PLAYER_MARKER_OFFLINE_COLOR = (128, 128, 128, 255)


def format_time(protobuf: AppMessage) -> RustTime:
    def convert_time(time) -> str:
        hours, minutes = divmod(time * 60, 60)

        return (
            f"{int(hours)}:0{int(minutes)}"
            if minutes <= 9
            else f"{int(hours)}:{int(minutes)}"
        )

    sunrise = convert_time(protobuf.response.time.sunrise)
    sunset = convert_time(protobuf.response.time.sunset)
    parsed_time = convert_time(protobuf.response.time.time)

    return RustTime(
        protobuf.response.time.day_length_minutes,
        sunrise,
        sunset,
        parsed_time,
        protobuf.response.time.time,
        protobuf.response.time.time_scale,
    )


def format_coord(x, y, map_size) -> Tuple[int, int]:
    y = map_size - y - 75
    x -= 75

    if x < 0:
        x = 0
    if x > map_size:
        x = map_size - 150
    if y < 0:
        y = 0
    if y > map_size:
        y = map_size - 150

    return x, y


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
    elif name == "4":
        with resources.path(ICONS_PATH, "chinook_blades.png") as path:
            blades = Image.open(path).convert("RGBA")
        blades = blades.resize((100, 100))
        icon.paste(blades, (64 - 50, 96 - 50), blades)
        icon.paste(blades, (64 - 50, 32 - 50), blades)
    elif name == "8":
        icon = icon.resize((200, 200))
        with resources.path(ICONS_PATH, "chinook_blades.png") as path:
            blades = Image.open(path).convert("RGBA")
        blades = blades.resize((200, 200))
        icon.paste(blades, (0, 0), blades)
    icon = icon.rotate(angle)
    return icon


def convert_monument(name: str, override_images: dict) -> Image.Image:
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


def entity_type_to_string(id) -> str:
    if id == 1:
        return "Switch"
    elif id == 2:
        return "Alarm"
    elif id == 3:
        return "Storage Monitor"
    else:
        raise ValueError("Not Valid type")


def _get_grid_x(x):
    counter = 1
    start_grid = 0
    while start_grid < x + GRID_DIAMETER:
        if start_grid <= x <= (start_grid + GRID_DIAMETER):
            # We're at the correct grid!
            return _number_to_letters(counter)

        counter += 1
        start_grid += GRID_DIAMETER


def _get_grid_y(y, map_size):
    counter = 1
    number_of_grids = map_size // GRID_DIAMETER
    start_grid = 0
    while start_grid < y + GRID_DIAMETER:
        if start_grid <= y <= (start_grid + GRID_DIAMETER):
            return number_of_grids - counter
        counter += 1
        start_grid += GRID_DIAMETER


def _number_to_letters(num):
    power, mod = divmod(num, 26)
    out = chr(64 + mod) if mod else (power, "Z")
    return _number_to_letters(power) + out if power else out


def _get_corrected_map_size(map_size):
    remainder = map_size % GRID_DIAMETER
    offset = GRID_DIAMETER - remainder
    return map_size - remainder if remainder < 120 else map_size + offset


def _is_outside_grid_system(x, y, map_size, offset=0):
    return (
        x < -offset or x > (map_size + offset) or y < -offset or y > (map_size + offset)
    )


class HackyBackwardsCompatCoordClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError("Index out of range")

    def __iter__(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return f"{self.x}{self.y}"

    def __str__(self):
        return self.__repr__()


def convert_xy_to_grid(
    coords: tuple, map_size: float, catch_out_of_bounds: bool = True
) -> HackyBackwardsCompatCoordClass:
    corrected_map_size = _get_corrected_map_size(map_size)

    grid_pos_letters = _get_grid_x(coords[0])
    grid_pos_number = str(int(_get_grid_y(coords[1], corrected_map_size)))

    return HackyBackwardsCompatCoordClass(grid_pos_letters, grid_pos_number)


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


def avatar_processing(
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
