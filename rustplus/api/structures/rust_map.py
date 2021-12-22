class RustMap:

    def __init__(self, data) -> None:
        
        self.width : int = data.width
        self.height : int = data.height
        self.jpgImage : bytes = data.jpgImage
        self.margin : int = data.oceanMargin
        self.monuments = [RustMonument(monument.token, monument.x, monument.y) for monument in data.monuments]
        self.background : str = None if data.background == "" else data.background

    def __str__(self) -> str:
        return "RustMap[width={}, height={}, jpgImage={}, margin={}, monuments={}, background={}]".format(self.width, self.height, len(self.jpgImage), self.margin, self.monuments, self.background)
        

class RustMonument:

    def __init__(self, token, x, y) -> None:
        
        self.token : str = token
        self.x : float = x
        self.y : float = y

    def __str__(self) -> str:
        return "RustMonument[token={}, x={}, y={}]"