import requests
import logging


class MagicValueGrabber:
    @staticmethod
    def get_magic_value() -> int:
        data = requests.get("https://companion-rust.facepunch.com/api/version")

        if data.status_code == 200:
            data = data.json()
            time = data.get("minPublishedTime", None)
            if time is not None:
                return time + 1

        logging.getLogger("rustplus.py").warning(
            "[Rustplus.py] Failed to get magic value from RustPlus Server"
        )
        return 9999999999999
