from importlib import resources
from PIL import Image
import logging
import string

from ..api.structures import RustTime

def format_time(protobuf) -> RustTime:

    def convert_time(time) -> str:

        HOURS, MINUTES = divmod(time * 60, 60)

        return f"{int(HOURS)}:0{int(MINUTES)}" if MINUTES <= 9 else f"{int(HOURS)}:{int(MINUTES)}"

    SUNRISE = convert_time(protobuf.response.time.sunrise)
    SUNSET = convert_time(protobuf.response.time.sunset)
    PARSED_TIME = convert_time(protobuf.response.time.time)

    return RustTime(protobuf.response.time.dayLengthMinutes, SUNRISE, SUNSET, PARSED_TIME, protobuf.response.time.time)

def format_cood(x, y, map_size) -> tuple:

    y = map_size - y - 75
    x -= 75

    if x < 0:
        x = 0
    if x > map_size:
        x = map_size - 150
    if y < 0:
        y = 0
    if y > map_size:
        y = map_size-150

    return x, y

def convert_marker(name, angle) -> Image:

    nameToFile = {
        "2" : "explosion.png",
        "4" : "chinook.png",
        "5" : "cargo.png",
        "6" : "crate.png",
    }
    
    with resources.path("rustplus.api.icons", nameToFile[name]) as path:
        icon = Image.open(path).convert("RGBA")
    if name == "6":
        icon = icon.resize((85,85))
    elif name == "2":
        icon = icon.resize((96,96))
    elif name == "4":
        with resources.path("rustplus.api.icons", "chinook_blades.png") as path:
            blades = Image.open(path).convert("RGBA")
        blades = blades.resize((100,100))
        icon.paste(blades, (64 - 50, 96 - 50), blades)
        icon.paste(blades, (64 - 50, 32 - 50), blades)
    icon = icon.rotate(angle)
    return icon

def convert_monument(name : str, override_images : dict) -> Image:

    name_to_file = {
        "train_tunnel_display_name" : "train.png",
        "supermarket" : "supermarket.png",
        "mining_outpost_display_name" : "mining_outpost.png",
        "gas_station" : "oxums.png",
        "fishing_village_display_name" : "fishing.png",
        "large_fishing_village_display_name" : "fishing.png",
        "lighthouse_display_name" : "lighthouse.png",
        "excavator" : "excavator.png",
        "water_treatment_plant_display_name" : "water_treatment.png",
        "train_yard_display_name" : "train_yard.png",
        "outpost" : "outpost.png",
        "bandit_camp" : "bandit.png",
        "junkyard_display_name" : "junkyard.png",
        "dome_monument_name" : "dome.png",
        "satellite_dish_display_name" : "satellite.png",
        "power_plant_display_name" : "power_plant.png",
        "military_tunnels_display_name" : "military_tunnels.png",
        "airfield_display_name" : "airfield.png",
        "launchsite" : "launchsite.png",
        "sewer_display_name" : "sewer.png",
        "oil_rig_small" : "small_oil_rig.png",
        "large_oil_rig" : "large_oil_rig.png",
        "underwater_lab" : "underwater_lab.png",
        "AbandonedMilitaryBase" : "desert_base.png"
    }

    overrideImages = override_images

    try:
        return overrideImages[name]
    except KeyError:
        pass
    
    if name in name_to_file:
        file_name = name_to_file[name]
        with resources.path("rustplus.api.icons", file_name) as path:
            icon = Image.open(path).convert("RGBA")
    elif "mining_quarry" in name or "harbor" in name or "stables" in name or "swamp" in name:
        if "mining_quarry" in name:
            file_name = "quarry.png"
        elif "harbor" in name:
            file_name = "harbour.png"
        elif "stables" in name:
            file_name = "stable.png"
        elif "swamp" in name:
            file_name = "swamp.png"
        with resources.path("rustplus.api.icons", file_name) as path:
            icon = Image.open(path).convert("RGBA")
    else:
        logging.getLogger("rustplus.py").info(f"{name} - Has no icon, report this as an issue")
        with resources.path("rustplus.api.icons", "icon.png") as path:
            icon = Image.open(path).convert("RGBA")
    return icon

def translate_id_to_stack(id : int) -> str:

    return {
        "-1018587433" : "Animal Fat",
        "609049394" : "Battery - Small",
        "1719978075" : "Bone Fragments",
        "634478325" : "CCTV Camera",
        "-1938052175" : "Charcoal",
        "-858312878" : "Cloth",
        "204391461" : "Coal :(",
        "-321733511" : "Crude Oil",
        "1568388703" : "Diesel Fuel",
        "1655979682" : "Empty Can of Beans",
        "-1557377697" : "Empty Tuna Can",
        "-592016202" : "Explosives",
        "-930193596" : "Fertilizer",
        "-265876753" : "Gun Powder",
        "317398316" : "High Quality Metal",
        "-1982036270" : "High Quality Metal Ore",
        "-1579932985" : "Horse Dung",
        "996293980" : "Human Skull",
        "1381010055" : "Leather",
        "-946369541" : "Low Grade Fuel",
        "69511070" : "Metal Fragments",
        "-4031221" : "Metal Ore",
        "-1779183908" : "Paper",
        "-804769727" : "Plant Fibre",
        "-544317637" : "Research Paper",
        "-277057363" : "Salt Water",
        "-932201673" : "Scrap",
        "-2099697608" : "Stones",
        "-1581843485" : "Sulfur",
        "-1157596551" : "Sulfur Ore",
        "1523195708" : "Targeting Computer",
        "-1779180711" : "Water",
        "2048317869" : "Wolf Skull",
        "-151838493" : "Wood"
    }[str(id)]

def entity_type_to_string(id) -> str:
    if id == 1:
        return "Switch"
    elif id == 2:
        return "Alarm"
    elif id == 3:
        return "Storage Monitor"
    else:
        raise ValueError("Not Valid type")

def convert_xy_to_grid(coords : tuple, map_size : float, catch_out_of_bounds : bool = True) -> tuple:

    GRIDSIZE = 146.25
    grids = list(string.ascii_uppercase) + [f"A{letter}" for letter in list(string.ascii_uppercase)]

    if coords[0] > map_size or coords[0] < 0 or coords[1] > map_size or coords[1] < 0:
        if catch_out_of_bounds:
            raise ValueError("Out of bounds")

    
    return grids[int(coords[0] // GRIDSIZE)], int((map_size - coords[1]) // GRIDSIZE)
