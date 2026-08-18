from typing import Any

import requests
import enum


class Realm(enum.Enum):
    Development = 0
    Staging = 1
    Production = 2


class NexusInterface:
    def __init__(self, endpoint: str):
        self.session = requests.Session()
        self.endpoint = endpoint

    def get_all_nexus(self, public_key: str, realm: Realm) -> Any | None:

        res = self.session.get(
            f"{self.endpoint}?publicKey={public_key}&realm={realm.value}"
        )

        if res.status_code == 200:
            return res.json()

        return None

    def get_nexus_info(self, nexus_id: int) -> Any | None:

        res = self.session.get(f"{self.endpoint}/{nexus_id}")

        if res.status_code == 200:
            return res.json()

        return None

    def get_nexus_map(self, nexus_id: int) -> Any | None:

        res = self.session.get(f"{self.endpoint}/{nexus_id}/map")

        if res.status_code == 200:
            return res.content

        return None
