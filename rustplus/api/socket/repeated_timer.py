from threading import Timer

class RepeatedTimer(object):

    def __init__(self, interval, function):

        self._timer = None
        self.interval = interval
        self.function = function
        self.is_running = False
        self.stopped = False
        self.start()

    def _run(self):

        if self.stopped:
            return
        self.is_running = False
        self.start()
        self.function()

    def start(self):

        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        
        self._timer.cancel()
        self.is_running = False
        self.stopped = True