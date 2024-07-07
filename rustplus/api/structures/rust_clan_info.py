from ..remote.rustplus_proto import (
    ClanInfo,
    ClanInfoRole,
    ClanInfoMember,
    ClanInfoInvite,
)
from typing import List


class RustClanRole:
    def __init__(self, role: ClanInfoRole) -> None:
        self._role_id: int = role.role_id
        self._rank: int = role.rank
        self._name: str = role.name
        self._can_set_motd: bool = role.can_set_motd
        self._can_set_logo: bool = role.can_set_logo
        self._can_invite: bool = role.can_invite
        self._can_kick: bool = role.can_kick
        self._can_promote: bool = role.can_promote
        self._can_demote: bool = role.can_demote
        self._can_set_player_notes: bool = role.can_set_player_notes
        self._can_access_logs: bool = role.can_access_logs

    @property
    def role_id(self) -> int:
        return self._role_id

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def name(self) -> str:
        return self._name

    @property
    def can_set_motd(self) -> bool:
        return self._can_set_motd

    @property
    def can_set_logo(self) -> bool:
        return self._can_set_logo

    @property
    def can_invite(self) -> bool:
        return self._can_invite

    @property
    def can_kick(self) -> bool:
        return self._can_kick

    @property
    def can_promote(self) -> bool:
        return self._can_promote

    @property
    def can_demote(self) -> bool:
        return self._can_demote

    @property
    def can_set_player_notes(self) -> bool:
        return self._can_set_player_notes

    @property
    def can_access_logs(self) -> bool:
        return self._can_access_logs


class RustClanMember:
    def __init__(self, member: ClanInfoMember) -> None:
        self._steam_id: int = member.steam_id
        self._role_id: int = member.role_id
        self._joined_time: int = member.joined
        self._last_seen: int = member.last_seen
        self._notes: str = member.notes
        self._online: bool = member.online

    @property
    def steam_id(self) -> int:
        return self._steam_id

    @property
    def role_id(self) -> int:
        return self._role_id

    @property
    def joined_time(self) -> int:
        return self._joined_time

    @property
    def last_seen(self) -> int:
        return self._last_seen

    @property
    def notes(self) -> str:
        return self._notes

    @property
    def online(self) -> bool:
        return self._online


class RustClanInvite:
    def __init__(self, invite: ClanInfoInvite) -> None:
        self._steam_id: int = invite.steam_id
        self._recruiter: int = invite.recruiter
        self._invited_time: int = invite.timestamp

    @property
    def steam_id(self) -> int:
        return self._steam_id

    @property
    def recruiter(self) -> int:
        return self._recruiter

    @property
    def invited_time(self) -> int:
        return self._invited_time


class RustClanInfo:
    def __init__(self, clan_info: ClanInfo) -> None:
        self._clan_id: int = clan_info.clan_id
        self._clan_name: str = clan_info.clan_name
        self._clan_time_created: int = clan_info.created
        self._creator: int = clan_info.creator
        self._motd: str = clan_info.motd
        self._motd_time_set: int = clan_info.motd_timestamp
        self._motd_author: int = clan_info.motd_author
        self._logo: bytes = clan_info.logo
        self._colour: int = clan_info.color
        self._roles: List[RustClanRole] = [
            RustClanRole(role) for role in clan_info.roles
        ]
        self._members: List[RustClanMember] = [
            RustClanMember(member) for member in clan_info.members
        ]
        self._invites: List[RustClanInvite] = [
            RustClanInvite(invite) for invite in clan_info.invites
        ]
        self._max_members: int = clan_info.max_member_count

    @property
    def clan_id(self) -> int:
        return self._clan_id

    @property
    def clan_name(self) -> str:
        return self._clan_name

    @property
    def clan_time_created(self) -> int:
        return self._clan_time_created

    @property
    def creator(self) -> int:
        return self._creator

    @property
    def motd(self) -> str:
        return self._motd

    @property
    def motd_time_set(self) -> int:
        return self._motd_time_set

    @property
    def motd_author(self) -> int:
        return self._motd_author

    @property
    def logo(self) -> bytes:
        return self._logo

    @property
    def colour(self) -> int:
        return self._colour

    @property
    def roles(self) -> List[RustClanRole]:
        return self._roles

    @property
    def members(self) -> List[RustClanMember]:
        return self._members

    @property
    def invites(self) -> List[RustClanInvite]:
        return self._invites

    @property
    def max_members(self) -> int:
        return self._max_members
