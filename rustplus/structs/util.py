import dataclasses


@dataclasses.dataclass
class Vector:
    x: float = 0
    y: float = 0


@dataclasses.dataclass
class RustAuthDetails:
    server_id: str = ""
    token: int = -1
