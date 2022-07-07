class RustInfo:
    def __init__(self, data) -> None:
        self._name: str = data.name
        self._url: str = data.url
        self._header_image: str = data.headerImage
        self._map: str = data.map
        self._size: int = data.mapSize
        self._wipe_time: int = data.wipeTime
        self._players: int = data.players
        self._max_players: int = data.maxPlayers
        self._queued_players: int = data.queuedPlayers
        self._seed: int = data.seed
        self._logo_image: str = data.logoImage

    @property
    def url(self) -> str:
        return self._url

    @property
    def name(self) -> str:
        return self._name

    @property
    def map(self) -> str:
        return self._map

    @property
    def size(self) -> int:
        return self._size

    @property
    def players(self) -> int:
        return self._players

    @property
    def max_players(self) -> int:
        return self._max_players

    @property
    def queued_players(self) -> int:
        return self._queued_players

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def wipe_time(self) -> int:
        return self._wipe_time

    @property
    def header_image(self) -> str:
        return self._header_image

    @property
    def logo_image(self) -> str:
        return self._logo_image

    def __str__(self) -> str:
        return (
            "RustInfo[url={}, name={}, map={}, size={}, players={}, max_players={}, queued_players={}, seed={}, "
            "wipe_time={}, header_image={}, logo_image={}]".format(
                self._url,
                self._name,
                self._map,
                self._size,
                self._players,
                self._max_players,
                self._queued_players,
                self._seed,
                self._wipe_time,
                self._header_image,
                self._logo_image,
            )
        )
