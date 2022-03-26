class RegisteredListener:
    def __init__(self, listener_id: str, data) -> None:
        self.listener_id = listener_id
        self.data = data

    def get_coro(self):
        return self.data[0]

    def __eq__(self, other):
        if isinstance(other, RegisteredListener):
            return self.listener_id == other.listener_id and self.data == other.data
        return False
