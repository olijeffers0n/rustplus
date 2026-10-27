import base64
import time
from dataclasses import dataclass, field

from websockets.typing import Subprotocol

from utils import deprecated


def _b64url(s: str) -> str:
    return base64.urlsafe_b64encode(s.encode()).decode().rstrip("=")


@dataclass(frozen=True)
class DirectEndpoint:
    ip: str
    port: int | None = None
    secure: bool = False

    def id(self) -> str:
        return f"{self.ip}:{self.port}" if self.port is not None else self.ip

    def uri(self) -> str:
        scheme = "wss" if self.secure else "ws"
        host = self.ip if self.port is None else f"{self.ip}:{self.port}"
        return f"{scheme}://{host}"

    @staticmethod
    def connect_kwargs() -> dict:
        return {}


@dataclass(frozen=True)
class RelayEndpoint:
    server_id: str
    # secret and short-lived: excluded from repr, eq and hash
    auth_token: str = field(repr=False, compare=False)
    host: str = "companion-rust.facepunch.com"
    version: int = int(time.time() * 1000)

    def id(self) -> str:
        return self.server_id

    def uri(self) -> str:
        return f"wss://{self.host}/socket/{self.server_id}?v={self.version}"

    def connect_kwargs(self) -> dict:
        return {
            "subprotocols": [
                Subprotocol("rustplus.auth.v1"),
                Subprotocol(_b64url(self.auth_token)),
            ],
            "origin": "https://app.playrust.com",
        }


Endpoint = DirectEndpoint | RelayEndpoint


@dataclass(frozen=True)
class ServerDetails:
    endpoint: Endpoint
    player_id: int
    player_token: int = field(repr=False)

    @classmethod
    @deprecated
    def direct(
        cls,
        ip: str,
        port: int | None,
        player_id: int,
        player_token: int,
        secure: bool = False,
    ):
        return cls(
            DirectEndpoint(str(ip), int(port) if port else None, secure),
            int(player_id),
            int(player_token),
        )

    @classmethod
    def facepunch(
        cls, server_id: str, auth_token: str, player_id: int, player_token: int
    ):
        return cls(
            RelayEndpoint(server_id, auth_token), int(player_id), int(player_token)
        )
