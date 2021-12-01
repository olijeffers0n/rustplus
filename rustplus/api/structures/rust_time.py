class RustTime:

    def __init__(self, day_length, sunrise, sunset, time, raw_time) -> None:

        self.day_length = day_length
        self.sunrise = sunrise
        self.sunset = sunset
        self.time = time
        self.raw_time = raw_time

    def __str__(self) -> str:
        return "RustTime[day_length={}, sunrise={}, sunset={}, time={}, raw_time={}]".format(self.day_length, self.sunset, self.sunset, self.time, self.raw_time)