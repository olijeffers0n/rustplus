class RegisteredListener:
    def __init__(self, listener_id: str, data) -> None:
        self.listener_id = str(listener_id)
        self.data = data

    def get_coro(self):
        return self.data[0]

    def __eq__(self, other):
        if isinstance(other, RegisteredListener):
            return self.listener_id == other.listener_id and self.data[0] == other.data[0]
        return False

    def __hash__(self):
        return hash((self.listener_id, self.data[0]))
