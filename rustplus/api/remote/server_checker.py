import logging
import threading
import requests


class ServerChecker:

    def __init__(self, ip: str, port: str) -> None:
        self.ip = ip
        self.port = port
        self.logger = logging.getLogger("rustplus.py")

    def run(self) -> None:
        threading.Thread(target=self._check_server, daemon=True).start()

    def _check_server(self) -> None:
        try:
            req = requests.post(f"https://companion-rust.facepunch.com/api/server/test_connection?address={self.ip}&port={self.port}")
            for msg in req.json()["messages"]:
                if "does not match your outgoing IP address" not in msg:
                    self.logger.warning(f"Error from server Checker:{msg}")
        except Exception:
            pass
