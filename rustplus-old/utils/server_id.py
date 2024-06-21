class ServerID:
    def __init__(self, ip, port, player_id, player_token) -> None:
        self.ip = ip
        self.port = port
        self.player_id = player_id
        self.player_token = player_token

    def __str__(self) -> str:
        return f"{self.ip}:{self.port} {self.player_id} {self.player_token}"

    def get_server_string(self) -> str:
        return f"{self.ip}:{self.port}"

    def __hash__(self):
        return hash(self.__str__())

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ServerID):
            return False

        return (
            self.ip == o.ip
            and self.port == o.port
            and self.player_id == o.player_id
            and self.player_token == o.player_token
        )
