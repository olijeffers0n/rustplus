from push_receiver import listen
from threading import Thread


class FCMListener:
    def __init__(self, data: dict = None):
        self.thread = None
        self.data = data

    def on_notification(self, obj, notification, data_message):
        pass

    def start(self):
        self.thread = Thread(target=self.__fcm_listen, daemon=True).start()

    def __fcm_listen(self):

        if self.data is None:
            raise ValueError("Data is None")

        listen(credentials=self.data["fcm_credentials"], callback=self.on_notification)
