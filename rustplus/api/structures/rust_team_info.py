from typing import List


class RustTeamMember:
    def __init__(self, data) -> None:
        self._steam_id: int = data.steamId
        self._name: str = data.name
        self._x: float = data.x
        self._y: float = data.y
        self._is_online: bool = data.isOnline
        self._spawn_time: int = data.spawnTime
        self._is_alive: bool = data.isAlive
        self._death_time: int = data.deathTime

    @property
    def steam_id(self) -> int:
        return self._steam_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def is_online(self) -> bool:
        return self._is_online

    @property
    def spawn_time(self) -> int:
        return self._spawn_time

    @property
    def is_alive(self) -> bool:
        return self._is_alive

    @property
    def death_time(self) -> int:
        return self._death_time

    def __str__(self) -> str:
        return "RustTeamMember[steam_id={}, name={}, x={}, y={}, is_online={}, spawn_time={}, is_alive={}, death_time={}]".format(
            self._steam_id,
            self._name,
            self._x,
            self._y,
            self._is_online,
            self._spawn_time,
            self._is_alive,
            self._death_time,
        )


class RustTeamNote:
    def __init__(self, data) -> None:
        self._type: int = data.type
        self._x: float = data.x
        self._y: float = data.y

    @property
    def type(self) -> int:
        return self._type

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def __str__(self) -> str:
        return "RustTeamNote[type={}, x={}, y={}]".format(self._type, self._x, self._y)


class RustTeamInfo:
    def __init__(self, data) -> None:
        self._leader_steam_id: int = data.leaderSteamId
        self._members = [RustTeamMember(member) for member in data.members]
        self._map_notes = [RustTeamNote(note) for note in data.mapNotes]
        self._leader_map_notes = [RustTeamNote(note) for note in data.leaderMapNotes]

    @property
    def leader_steam_id(self) -> int:
        return self._leader_steam_id

    @property
    def members(self) -> List[RustTeamMember]:
        return self._members

    @property
    def map_notes(self) -> List[RustTeamNote]:
        return self._map_notes

    @property
    def leader_map_notes(self) -> List[RustTeamNote]:
        return self._leader_map_notes

    def __str__(self) -> str:
        return "RustTeamInfo[leader_steam_id={}, members={}, map_notes={}, leader_map_notes={}]".format(
            self._leader_steam_id,
            self._members,
            self._map_notes,
            self._leader_map_notes,
        )
