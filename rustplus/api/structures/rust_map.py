class RustMap:

    def __init__(self, data) -> None:
        
        self.width = data.width
        self.height = data.height
        self.jpgImage = data.jpgImage
        self.margin = data.oceanMargin
        self.monuments = [RustMonument(monument.token, monument.x, monument.y) for monument in data.monuments]
        self.background = None if data.background == "" else data.background

    def __str__(self) -> str:
        return "RustMap[width={}, height={}, jpgImage={}, margin={}, monuments={}, background={}]".format(self.width, self.height, len(self.jpgImage), self.margin, self.monuments, self.background)
        

class RustMonument:

    def __init__(self, token, x, y) -> None:
        
        self.token = token
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return "RustMonument[token={}, x={}, y={}]"