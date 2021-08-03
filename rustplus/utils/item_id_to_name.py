class IdToName:

    def __init__(self) -> None:
        self.codes = {
                "-1018587433" : "Animal Fat",
                "609049394" : "Battery - Small",
                "1719978075" : "Bone Fragments",
                "634478325" : "CCTV Camera",
                "-1938052175" : "Charcoal",
                "-858312878" : "Cloth",
                "204391461" : "Coal",
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
                "-946369541" : "Low Grade Fuel",
                "69511070" : "Metal Fragments",
                "-4031221" : "Metal Ore",
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
            }

    def translate(self, id : int) -> str:
        return self.codes[str(id)]