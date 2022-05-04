import asyncio
from typing import List, Type
from .conversation_prompt import ConversationPrompt


class Conversation:

    def __init__(self, api, target: int = None, prompts: List[Type[ConversationPrompt]] = None, register=None) -> None:

        if target is None:
            raise ValueError("target must be specified")
        self._target = target

        if prompts is None:
            self._prompts = []
        else:
            self._prompts = prompts

        self._answers = []
        self._seq = 0
        self._api = api
        self._loop = None
        self._register = register

    def add_prompt(self, prompt: Type[ConversationPrompt]) -> None:
        self._prompts.append(prompt)

    def add_all_prompts(self, prompts: List[Type[ConversationPrompt]]) -> None:
        self._prompts.extend(prompts)

    def has_next(self) -> bool:
        return self._seq+1 < len(self._prompts)

    def get_current_prompt(self) -> ConversationPrompt:
        return self._prompts[self._seq](self)

    def increment_prompt(self) -> None:
        self._seq += 1

    async def send_prompt(self, message: str) -> None:
        if self._api.remote.ws is not None:
            self._api.remote.ws.outgoing_conversation_messages.append(message)
        await self._api.send_team_message(message)

    async def start(self) -> None:
        self._register(self._target, self)
        self._loop = asyncio.get_event_loop_policy().get_event_loop()
        await self.send_prompt(await self._prompts[0](self).prompt())

    def run_coro(self, coro, args):
        return asyncio.run_coroutine_threadsafe(coro(*args), self._loop).result()

    def get_answers(self) -> List[str]:
        return self._answers


