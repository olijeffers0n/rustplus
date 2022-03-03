class RegisteredListener:
    def __init__(self, name: str, data) -> None:
        self.listener_id = name
        self.data = data

    def get_coro(self):
        return self.data[0]
