from importlib import resources
from PIL import Image

class MonumentNameToImage:

    def __init__(self, overrideImages : dict = {}) -> None:
        self.name_to_file = {
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

        self.overrideImages = overrideImages

    def convert(self, name : str) -> Image:

        try:
            return self.overrideImages[name]
        except KeyError as e:
            pass
        
        if name in self.name_to_file:
            file_name = self.name_to_file[name]
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
            print(name + " - Has no icon, defaulting...")
            with resources.path("rustplus.api.icons", "icon.png") as path:
                icon = Image.open(path).convert("RGBA")
        return icon