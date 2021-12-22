class RustInfo:

    def __init__(self, data) -> None:
        
        self.url : str = data.url
        self.name : str = data.name
        self.map : str = data.map
        self.size : int = data.mapSize
        self.players : int = data.players
        self.max_players : int = data.maxPlayers
        self.queued_players : int = data.queuedPlayers
        self.seed : int = data.seed

    def __str__(self) -> str:
        return "RustInfo[url={}, name={}, map={}, size={}, players={}, max_players={}, queued_players={}, seed={}]".format(self.url, self.name, self.map, self.size, self.players, self.max_players, self.queued_players, self.seed)