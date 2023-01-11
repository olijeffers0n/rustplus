class EventLoopManager:

    _loop = None

    @staticmethod
    def get_loop():
        if EventLoopManager._loop is None:
            raise RuntimeError("Event loop is not set")

        if EventLoopManager._loop.is_closed():
            raise RuntimeError("Event loop is not running")

        return EventLoopManager._loop
