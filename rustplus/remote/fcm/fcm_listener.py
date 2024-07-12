from push_receiver import PushReceiver
from threading import Thread


class FCMListener:
    def __init__(self, data: dict = None) -> None:
        self.thread = None
        self.data = data
        self._push_listener = PushReceiver(credentials=self.data["fcm_credentials"])

    def on_notification(self, obj, notification, data_message) -> None:
        pass

    def start(self, daemon=False) -> None:
        self.thread = Thread(target=self.__fcm_listen, daemon=daemon).start()

    def __fcm_listen(self) -> None:
        if self.data is None:
            raise ValueError("Data is None")

        self._push_listener.listen(callback=self.on_notification)
