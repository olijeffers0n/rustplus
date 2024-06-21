class ConversationPrompt:
    def __init__(self, conversation) -> None:
        self.conversation = conversation

    async def prompt(self) -> str:
        return ""

    async def on_response(self, response) -> None:
        pass

    async def on_finish(self) -> str:
        return ""
