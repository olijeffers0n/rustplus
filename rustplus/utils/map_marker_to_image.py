from importlib import resources
from PIL import Image

class MapMarkerConverter:

    def __init__(self) -> None:
        self.nameToFile = {
            "2" : "explosion.png",
            "4" : "chinook.png",
            "5" : "cargo.png",
            "6" : "crate.png",
        }

    def convert(self, name, angle) -> Image:
        
        with resources.path("rustplus.api.icons", self.nameToFile[name]) as path:
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
