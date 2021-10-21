class RustTeamInfo:

    def __init__(self, data) -> None:
        
        self.leaderSteamId = data.leaderSteamId
        self.members = [RustTeamMember(member) for member in data.members]
        self.mapNotes = [RustTeamNote(note) for note in data.mapNotes]
        self.leaderMapNotes = [RustTeamNote(note) for note in data.leaderMapNotes]

    def __str__(self) -> str:
        return "RustTeamInfo[leaderSteamId={}, members={}, mapNotes={}, leaderMapNotes={}]".format(self.leaderSteamId, self.members, self.mapNotes, self.leaderMapNotes)

class RustTeamMember:

    def __init__(self, data) -> None:
        
        self.steamId = data.steamId
        self.name = data.name
        self.x = data.x
        self.y = data.y
        self.isOnline = data.isOnline
        self.spawnTime = data.spawnTime
        self.isAlive = data.isAlive
        self.deathTime = data.deathTime

    def __str__(self) -> str:
        return "RustTeamMember[steamId={}, name={}, x={}, y={}, isOnline={}, spawnTime={}, isAlive={}, deathTime={}]".format(self.steamId, self.name, self.x, self.y, self.isOnline, self.spawnTime, self.isAlive, self.deathTime)

class RustTeamNote:

    def __init__(self, data) -> None:
        
        self.type = data.type
        self.x = data.x
        self.y = data.y

    def __str__(self) -> str:
        return "RustTeamNote[type={}, x={}, y={}]".format(self.type, self.x, self.y)