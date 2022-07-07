from importlib import resources
from PIL import Image
import logging
import string

from ..api.structures import RustTime

icons_path = "rustplus.api.icons"


def format_time(protobuf) -> RustTime:
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
        protobuf.response.time.dayLengthMinutes,
        sunrise,
        sunset,
        parsed_time,
        protobuf.response.time.time,
    )


def format_coord(x, y, map_size) -> tuple:
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


def convert_marker(name, angle) -> Image:
    name_to_file = {
        "2": "explosion.png",
        "4": "chinook.png",
        "5": "cargo.png",
        "6": "crate.png",
        "8": "patrol.png",
    }

    with resources.path(icons_path, name_to_file[name]) as path:
        icon = Image.open(path).convert("RGBA")
    if name == "6":
        icon = icon.resize((85, 85))
    elif name == "2":
        icon = icon.resize((96, 96))
    elif name == "4":
        with resources.path(icons_path, "chinook_blades.png") as path:
            blades = Image.open(path).convert("RGBA")
        blades = blades.resize((100, 100))
        icon.paste(blades, (64 - 50, 96 - 50), blades)
        icon.paste(blades, (64 - 50, 32 - 50), blades)
    elif name == "8":
        icon = icon.resize((200, 200))
        with resources.path(icons_path, "chinook_blades.png") as path:
            blades = Image.open(path).convert("RGBA")
        blades = blades.resize((200, 200))
        icon.paste(blades, (0, 0), blades)
    icon = icon.rotate(angle)
    return icon


def convert_monument(name: str, override_images: dict) -> Image:
    name_to_file = {
        "train_tunnel_display_name": "train.png",
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
    }

    try:
        return override_images[name]
    except KeyError:
        pass

    if name in name_to_file:
        file_name = name_to_file[name]
        with resources.path(icons_path, file_name) as path:
            icon = Image.open(path).convert("RGBA")
    elif (
        "mining_quarry" in name
        or "harbor" in name
        or "stables" in name
        or "swamp" in name
        or "arctic_base" in name
    ):
        if "mining_quarry" in name:
            file_name = "quarry.png"
        elif "harbor" in name:
            file_name = "harbour.png"
        elif "stables" in name:
            file_name = "stable.png"
        elif "swamp" in name:
            file_name = "swamp.png"
        elif "arctic_base" in name:
            file_name = "arctic_base.png"
        with resources.path(icons_path, file_name) as path:
            icon = Image.open(path).convert("RGBA")
    else:
        logging.getLogger("rustplus.py").info(
            f"{name} - Has no icon, report this as an issue"
        )
        with resources.path(icons_path, "icon.png") as path:
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


def convert_xy_to_grid(
    coords: tuple, map_size: float, catch_out_of_bounds: bool = True
) -> tuple:
    grid_size = 146.3
    grids = list(string.ascii_uppercase) + [
        f"A{letter}" for letter in list(string.ascii_uppercase)
    ]

    if coords[0] > map_size or coords[0] < 0 or coords[1] > map_size or coords[1] < 0:
        if catch_out_of_bounds:
            raise ValueError("Out of bounds")

    return grids[int(coords[0] // grid_size)], int((map_size - coords[1]) // grid_size)
