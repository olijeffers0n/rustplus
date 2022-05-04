from .conversation import Conversation


class ConversationFactory:

    def __init__(self, api):
        self.api = api
        self.conversations = {}

    def create_conversation(self, target_user: int) -> Conversation:

        if target_user in self.conversations:
            raise ValueError("Conversation already exists")

        return Conversation(api=self.api, target=target_user, register=self._register_conversation)

    def _register_conversation(self, steamid, convo: Conversation) -> None:
        self.conversations[steamid] = convo

    def has_conversation(self, target_user: int) -> bool:
        return target_user in self.conversations

    def get_conversation(self, target_user: int) -> Conversation:
        return self.conversations[target_user]

    def abort_conversation(self, target_user: int) -> None:
        try:
            del self.conversations[target_user]
        except KeyError:
            pass
