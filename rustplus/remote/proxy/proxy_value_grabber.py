import requests
import logging
import time


class ProxyValueGrabber:

    VALUE = -1
    LAST_FETCHED = -1

    @staticmethod
    def get_value() -> int:

        if (
            ProxyValueGrabber.VALUE != -1
            and ProxyValueGrabber.LAST_FETCHED >= time.time() - 600
        ):
            return ProxyValueGrabber.VALUE

        data = requests.get("https://companion-rust.facepunch.com/api/version")

        if data.status_code == 200:
            publish_time = data.json().get("minPublishedTime", None)
            if publish_time is not None:
                ProxyValueGrabber.VALUE = publish_time + 1
                ProxyValueGrabber.LAST_FETCHED = time.time()
                return ProxyValueGrabber.VALUE

        logging.getLogger("rustplus.py").warning(
            "Failed to get magic value from RustPlus Server"
        )
        return 9999999999999
