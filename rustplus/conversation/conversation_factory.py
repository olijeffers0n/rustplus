import time
from threading import Thread

from .conversation import Conversation


class ConversationFactory:
    def __init__(self, api):
        self.api = api
        self.conversations = {}
        self.expires = {}
        self.gc_thread = Thread(target=self.garbage_collect, daemon=True)
        self.gc_thread.start()

    def create_conversation(self, steamid: int) -> Conversation:

        if steamid in self.conversations:
            raise ValueError("Conversation already exists")

        return Conversation(
            api=self.api, target=steamid, register=self._register_conversation
        )

    def _register_conversation(self, steamid, convo: Conversation) -> None:
        self.conversations[steamid] = convo
        self.expires[steamid] = time.time() + 60 * 5

    def has_conversation(self, steamid: int) -> bool:
        return steamid in self.conversations

    def get_conversation(self, steamid: int) -> Conversation:
        return self.conversations[steamid]

    def abort_conversation(self, steamid: int) -> None:
        try:
            del self.conversations[steamid]
            del self.expires[steamid]
        except KeyError:
            pass

    def garbage_collect(self) -> None:
        while True:
            to_remove = []
            for steamid, expire_time in self.expires.items():
                if expire_time < time.time():
                    to_remove.append(steamid)

            for steamid in to_remove:
                self.abort_conversation(steamid)

            time.sleep(5)
