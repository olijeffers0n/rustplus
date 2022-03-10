class RustTime:
    def __init__(self, day_length, sunrise, sunset, time, raw_time) -> None:
        self._day_length: float = day_length
        self._sunrise: str = sunrise
        self._sunset: str = sunset
        self._time: str = time
        self._raw_time: float = raw_time

    @property
    def day_length(self) -> float:
        return self._day_length

    @property
    def sunrise(self) -> str:
        return self._sunrise

    @property
    def sunset(self) -> str:
        return self._sunset

    @property
    def time(self) -> str:
        return self._time

    @property
    def raw_time(self) -> float:
        return self._raw_time

    def __str__(self) -> str:
        return "RustTime[day_length={}, sunrise={}, sunset={}, time={}, raw_time={}]".format(
            self._day_length, self._sunrise, self._sunset, self._time, self._raw_time
        )
