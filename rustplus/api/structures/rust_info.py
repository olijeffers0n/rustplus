class RustInfo:

    def __init__(self, data) -> None:
        
        self.url = data.url
        self.name = data.name
        self.map = data.map
        self.size = data.mapSize
        self.players = data.players
        self.max_players = data.maxPlayers
        self.queued_players = data.queuedPlayers
        self.seed = data.seed

    def __str__(self) -> str:
        return "RustInfo[url={}, name={}, map={}, size={}, players={}, max_players={}, queued_players={}, seed={}]".format(self.url, self.name, self.map, self.size, self.players, self.max_players, self.queued_players, self.seed)