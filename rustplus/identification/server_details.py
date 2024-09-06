from typing import Union


class ServerDetails:
    def __init__(
        self,
        ip: str,
        port: Union[str, int, None],
        player_id: int,
        player_token: int,
        secure: bool = False,
    ) -> None:
        self.ip = str(ip)
        self.port = str(port)
        self.player_id = int(player_id)
        self.player_token = int(player_token)
        self.secure = secure

    def get_server_string(self) -> str:
        if self.port is None:
            return f"{self.ip}"
        return f"{self.ip}:{self.port}"

    def __str__(self) -> str:
        return f"{self.ip}:{self.port} {self.player_id} {self.player_token}"

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ServerDetails):
            return False

        return (
            self.ip == o.ip
            and self.port == o.port
            and self.player_id == o.player_id
            and self.player_token == o.player_token
        )
