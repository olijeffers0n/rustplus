from typing import List


class RustMonument:
    def __init__(self, token, x, y) -> None:
        self._token: str = token
        self._x: float = x
        self._y: float = y

    @property
    def token(self) -> str:
        return self._token

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def __str__(self) -> str:
        return "RustMonument[token={}, x={}, y={}]".format(
            self._token, self._x, self._y
        )


class RustMap:
    def __init__(self, data) -> None:
        self._width: int = data.width
        self._height: int = data.height
        self._jpg_image: bytes = data.jpgImage
        self._margin: int = data.oceanMargin
        self._monuments = [
            RustMonument(monument.token, monument.x, monument.y)
            for monument in data.monuments
        ]
        self._background: str = None if data.background == "" else data.background

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def jpg_image(self) -> bytes:
        return self._jpg_image

    @property
    def margin(self) -> int:
        return self._margin

    @property
    def monuments(self) -> List[RustMonument]:
        return self._monuments

    @property
    def background(self) -> str:
        return self._background

    def __str__(self) -> str:
        return "RustMap[width={}, height={}, jpg_image={}, margin={}, monuments={}, background={}]".format(
            self._width,
            self._height,
            len(self._jpg_image),
            self._margin,
            self._monuments,
            self._background,
        )
