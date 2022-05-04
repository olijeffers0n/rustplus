import asyncio
from typing import List, Type
from .conversation_prompt import ConversationPrompt


class Conversation:

    def __init__(self, api, target: int = None, prompts: List[Type[ConversationPrompt]] = None, register=None) -> None:

        if target is None:
            raise ValueError("target must be specified")
        self.target = target

        if prompts is None:
            self.prompts = []
        else:
            self.prompts = prompts

        self.answers = []
        self.seq = 0
        self.api = api
        self.loop = None
        self.register = register

    def add_prompt(self, prompt: Type[ConversationPrompt]) -> None:
        self.prompts.append(prompt)

    def add_all_prompts(self, prompts: List[Type[ConversationPrompt]]) -> None:
        self.prompts.extend(prompts)

    def has_next(self) -> bool:
        return self.seq+1 < len(self.prompts)

    def get_current_prompt(self) -> ConversationPrompt:
        return self.prompts[self.seq](self)

    def increment_prompt(self) -> None:
        self.seq += 1

    async def send_prompt(self, message: str) -> None:
        if self.api.remote.ws is not None:
            self.api.remote.ws.outgoing_conversation_messages.append(message)
        await self.api.send_team_message(message)

    async def start(self) -> None:
        self.register(self.target, self)
        self.loop = asyncio.get_event_loop_policy().get_event_loop()
        await self.send_prompt(await self.prompts[0](self).prompt())

    def run_coro(self, coro, args):
        return asyncio.run_coroutine_threadsafe(coro(*args), self.loop).result()

    def get_answers(self) -> List[str]:
        return self.answers


