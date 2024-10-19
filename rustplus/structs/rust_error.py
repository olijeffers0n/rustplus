from .serialization import Serializable


class RustError(Serializable):

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
