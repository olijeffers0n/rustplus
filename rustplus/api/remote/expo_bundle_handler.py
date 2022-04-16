import requests
import logging
import json
from datetime import datetime


class MagicValueGrabber:
    @staticmethod
    def get_magic_value() -> int:

        try:
            data = requests.get(
                "https://exp.host/@facepunch/RustCompanion",
                headers={
                    "Exponent-SDK-Version": "40.0.0",  # These are the two lines that determine the version of data that
                    "Exponent-Version": "0.0.21",  # you receive as far as I can tell from my limited debugging. As of
                    # now (8th April 2022), this is the latest
                    "Exponent-Platform": "android",
                    "Accept": "application/expo+json,application/json",
                    "Expo-Release-Channel": "default",
                    "Expo-Api-Version": "1",
                    "Expo-Client-Environment": "STANDALONE",
                    "Exponent-Accept-Signature": "true",
                    "Expo-JSON-Error": "true",
                    "Host": "exp.host",
                    "User-Agent": "okhttp/3.12.1",
                },
            )

            halves = (
                str(json.loads(data.json()["manifestString"])["publishedTime"])
                .replace("Z", "")
                .split("T")
            )

            year, month, day = halves[0].split("-")
            hour, minute, second = halves[1].split(":")

            dt = datetime(int(year), int(month), int(day), int(hour), int(minute), 0)

            return int(
                ((dt - datetime.utcfromtimestamp(0)).total_seconds() * 1000.0)
                + float(second) * 1000
            )
        except Exception:
            logging.getLogger("rustplus.py").warning(
                "[Rustplus.py] Failed to get magic value from RustPlus Server"
            )
            return 1641359159846
