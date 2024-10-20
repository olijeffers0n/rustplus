import logging
from typing import Any

from .serialization import Serializable


class RustError(Serializable):

    LOGGER = logging.getLogger("rustplus.py")

    def __init__(self, method: str, reason: str) -> None:
        self._method = method
        self._reason = reason

    @property
    def method(self) -> str:
        return self._method

    @property
    def reason(self) -> str:
        return self._reason

    def __str__(self) -> str:
        return f"Error Propagating from {self._method}: {self._reason}"

    def __getattr__(self, attr_name: str) -> Any:
        if attr_name in self.__dict__:
            return self.__dict__[attr_name]

        # This means we are gonna chuck the error in the user's face
        self.LOGGER.error(
            f"An Unhandled Error has occurred over the {self._method} method, reason: {self.reason}"
        )
