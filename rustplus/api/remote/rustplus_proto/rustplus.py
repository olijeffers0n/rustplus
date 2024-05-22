# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: rustplus.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import List

import betterproto


class AppEntityType(betterproto.Enum):
    Switch = 1
    Alarm = 2
    StorageMonitor = 3


class AppMarkerType(betterproto.Enum):
    Undefined = 0
    Player = 1
    Explosion = 2
    VendingMachine = 3
    CH47 = 4
    CargoShip = 5
    Crate = 6
    GenericRadius = 7
    PatrolHelicopter = 8


class AppCameraRaysEntityType(betterproto.Enum):
    Tree = 1
    Player = 2


@dataclass
class Vector2(betterproto.Message):
    x: float = betterproto.float_field(1)
    y: float = betterproto.float_field(2)


@dataclass
class Vector3(betterproto.Message):
    x: float = betterproto.float_field(1)
    y: float = betterproto.float_field(2)
    z: float = betterproto.float_field(3)


@dataclass
class Vector4(betterproto.Message):
    x: float = betterproto.float_field(1)
    y: float = betterproto.float_field(2)
    z: float = betterproto.float_field(3)
    w: float = betterproto.float_field(4)


@dataclass
class Half3(betterproto.Message):
    x: int = betterproto.uint32_field(1)
    y: int = betterproto.uint32_field(2)
    z: int = betterproto.uint32_field(3)


@dataclass
class Color(betterproto.Message):
    r: float = betterproto.float_field(1)
    g: float = betterproto.float_field(2)
    b: float = betterproto.float_field(3)
    a: float = betterproto.float_field(4)


@dataclass
class Ray(betterproto.Message):
    origin: "Vector3" = betterproto.message_field(1)
    direction: "Vector3" = betterproto.message_field(2)


@dataclass
class ClanActionResult(betterproto.Message):
    request_id: int = betterproto.int32_field(1)
    result: int = betterproto.int32_field(2)
    has_clan_info: bool = betterproto.bool_field(3)
    clan_info: "ClanInfo" = betterproto.message_field(4)


@dataclass
class ClanInfo(betterproto.Message):
    clan_id: int = betterproto.int64_field(1)
    name: str = betterproto.string_field(2)
    created: int = betterproto.int64_field(3)
    creator: int = betterproto.uint64_field(4)
    motd: str = betterproto.string_field(5)
    motd_timestamp: int = betterproto.int64_field(6)
    motd_author: int = betterproto.uint64_field(7)
    logo: bytes = betterproto.bytes_field(8)
    color: int = betterproto.sint32_field(9)
    roles: List["ClanInfoRole"] = betterproto.message_field(10)
    members: List["ClanInfoMember"] = betterproto.message_field(11)
    invites: List["ClanInfoInvite"] = betterproto.message_field(12)
    max_member_count: int = betterproto.int32_field(13)


@dataclass
class ClanInfoRole(betterproto.Message):
    role_id: int = betterproto.int32_field(1)
    rank: int = betterproto.int32_field(2)
    name: str = betterproto.string_field(3)
    can_set_motd: bool = betterproto.bool_field(4)
    can_set_logo: bool = betterproto.bool_field(5)
    can_invite: bool = betterproto.bool_field(6)
    can_kick: bool = betterproto.bool_field(7)
    can_promote: bool = betterproto.bool_field(8)
    can_demote: bool = betterproto.bool_field(9)
    can_set_player_notes: bool = betterproto.bool_field(10)
    can_access_logs: bool = betterproto.bool_field(11)


@dataclass
class ClanInfoMember(betterproto.Message):
    steam_id: int = betterproto.uint64_field(1)
    role_id: int = betterproto.int32_field(2)
    joined: int = betterproto.int64_field(3)
    last_seen: int = betterproto.int64_field(4)
    notes: str = betterproto.string_field(5)
    online: bool = betterproto.bool_field(6)


@dataclass
class ClanInfoInvite(betterproto.Message):
    steam_id: int = betterproto.uint64_field(1)
    recruiter: int = betterproto.uint64_field(2)
    timestamp: int = betterproto.int64_field(3)


@dataclass
class ClanLog(betterproto.Message):
    clan_id: int = betterproto.int64_field(1)
    log_entries: List["ClanLogEntry"] = betterproto.message_field(2)


@dataclass
class ClanLogEntry(betterproto.Message):
    timestamp: int = betterproto.int64_field(1)
    event_key: str = betterproto.string_field(2)
    arg1: str = betterproto.string_field(3)
    arg2: str = betterproto.string_field(4)
    arg3: str = betterproto.string_field(5)
    arg4: str = betterproto.string_field(6)


@dataclass
class ClanInvitations(betterproto.Message):
    invitations: List["ClanInvitationsInvitation"] = betterproto.message_field(1)


@dataclass
class ClanInvitationsInvitation(betterproto.Message):
    clan_id: int = betterproto.int64_field(1)
    recruiter: int = betterproto.uint64_field(2)
    timestamp: int = betterproto.int64_field(3)


@dataclass
class AppRequest(betterproto.Message):
    seq: int = betterproto.uint32_field(1)
    player_id: int = betterproto.uint64_field(2)
    player_token: int = betterproto.int32_field(3)
    entity_id: int = betterproto.uint32_field(4)
    get_info: "AppEmpty" = betterproto.message_field(8)
    get_time: "AppEmpty" = betterproto.message_field(9)
    get_map: "AppEmpty" = betterproto.message_field(10)
    get_team_info: "AppEmpty" = betterproto.message_field(11)
    get_team_chat: "AppEmpty" = betterproto.message_field(12)
    send_team_message: "AppSendMessage" = betterproto.message_field(13)
    get_entity_info: "AppEmpty" = betterproto.message_field(14)
    set_entity_value: "AppSetEntityValue" = betterproto.message_field(15)
    check_subscription: "AppEmpty" = betterproto.message_field(16)
    set_subscription: "AppFlag" = betterproto.message_field(17)
    get_map_markers: "AppEmpty" = betterproto.message_field(18)
    promote_to_leader: "AppPromoteToLeader" = betterproto.message_field(20)
    get_clan_info: "AppEmpty" = betterproto.message_field(21)
    set_clan_motd: "AppSendMessage" = betterproto.message_field(22)
    get_clan_chat: "AppEmpty" = betterproto.message_field(23)
    send_clan_message: "AppSendMessage" = betterproto.message_field(24)
    get_nexus_auth: "AppGetNexusAuth" = betterproto.message_field(25)
    camera_subscribe: "AppCameraSubscribe" = betterproto.message_field(30)
    camera_unsubscribe: "AppEmpty" = betterproto.message_field(31)
    camera_input: "AppCameraInput" = betterproto.message_field(32)


@dataclass
class AppMessage(betterproto.Message):
    response: "AppResponse" = betterproto.message_field(1)
    broadcast: "AppBroadcast" = betterproto.message_field(2)


@dataclass
class AppResponse(betterproto.Message):
    seq: int = betterproto.uint32_field(1)
    success: "AppSuccess" = betterproto.message_field(4)
    error: "AppError" = betterproto.message_field(5)
    info: "AppInfo" = betterproto.message_field(6)
    time: "AppTime" = betterproto.message_field(7)
    map: "AppMap" = betterproto.message_field(8)
    team_info: "AppTeamInfo" = betterproto.message_field(9)
    team_chat: "AppTeamChat" = betterproto.message_field(10)
    entity_info: "AppEntityInfo" = betterproto.message_field(11)
    flag: "AppFlag" = betterproto.message_field(12)
    map_markers: "AppMapMarkers" = betterproto.message_field(13)
    clan_info: "AppClanInfo" = betterproto.message_field(15)
    clan_chat: "AppClanChat" = betterproto.message_field(16)
    nexus_auth: "AppNexusAuth" = betterproto.message_field(17)
    camera_subscribe_info: "AppCameraInfo" = betterproto.message_field(20)


@dataclass
class AppBroadcast(betterproto.Message):
    team_changed: "AppTeamChanged" = betterproto.message_field(4)
    team_message: "AppNewTeamMessage" = betterproto.message_field(5)
    entity_changed: "AppEntityChanged" = betterproto.message_field(6)
    clan_changed: "AppClanChanged" = betterproto.message_field(7)
    clan_message: "AppNewClanMessage" = betterproto.message_field(8)
    camera_rays: "AppCameraRays" = betterproto.message_field(10)


@dataclass
class AppEmpty(betterproto.Message):
    pass


@dataclass
class AppSendMessage(betterproto.Message):
    message: str = betterproto.string_field(1)


@dataclass
class AppSetEntityValue(betterproto.Message):
    value: bool = betterproto.bool_field(1)


@dataclass
class AppPromoteToLeader(betterproto.Message):
    steam_id: int = betterproto.uint64_field(1)


@dataclass
class AppGetNexusAuth(betterproto.Message):
    app_key: str = betterproto.string_field(1)


@dataclass
class AppSuccess(betterproto.Message):
    pass


@dataclass
class AppError(betterproto.Message):
    error: str = betterproto.string_field(1)


@dataclass
class AppFlag(betterproto.Message):
    value: bool = betterproto.bool_field(1)


@dataclass
class AppInfo(betterproto.Message):
    name: str = betterproto.string_field(1)
    header_image: str = betterproto.string_field(2)
    url: str = betterproto.string_field(3)
    map: str = betterproto.string_field(4)
    map_size: int = betterproto.uint32_field(5)
    wipe_time: int = betterproto.uint32_field(6)
    players: int = betterproto.uint32_field(7)
    max_players: int = betterproto.uint32_field(8)
    queued_players: int = betterproto.uint32_field(9)
    seed: int = betterproto.uint32_field(10)
    salt: int = betterproto.uint32_field(11)
    logo_image: str = betterproto.string_field(12)
    nexus: str = betterproto.string_field(13)
    nexus_id: int = betterproto.int32_field(14)
    nexus_zone: str = betterproto.string_field(15)
    cameras_enabled: bool = betterproto.bool_field(16)


@dataclass
class AppTime(betterproto.Message):
    day_length_minutes: float = betterproto.float_field(1)
    time_scale: float = betterproto.float_field(2)
    sunrise: float = betterproto.float_field(3)
    sunset: float = betterproto.float_field(4)
    time: float = betterproto.float_field(5)


@dataclass
class AppMap(betterproto.Message):
    width: int = betterproto.uint32_field(1)
    height: int = betterproto.uint32_field(2)
    jpg_image: bytes = betterproto.bytes_field(3)
    ocean_margin: int = betterproto.int32_field(4)
    monuments: List["AppMapMonument"] = betterproto.message_field(5)
    background: str = betterproto.string_field(6)


@dataclass
class AppMapMonument(betterproto.Message):
    token: str = betterproto.string_field(1)
    x: float = betterproto.float_field(2)
    y: float = betterproto.float_field(3)


@dataclass
class AppEntityInfo(betterproto.Message):
    type: "AppEntityType" = betterproto.enum_field(1)
    payload: "AppEntityPayload" = betterproto.message_field(3)


@dataclass
class AppEntityPayload(betterproto.Message):
    value: bool = betterproto.bool_field(1)
    items: List["AppEntityPayloadItem"] = betterproto.message_field(2)
    capacity: int = betterproto.int32_field(3)
    has_protection: bool = betterproto.bool_field(4)
    protection_expiry: int = betterproto.uint32_field(5)


@dataclass
class AppEntityPayloadItem(betterproto.Message):
    item_id: int = betterproto.int32_field(1)
    quantity: int = betterproto.int32_field(2)
    item_is_blueprint: bool = betterproto.bool_field(3)


@dataclass
class AppTeamInfo(betterproto.Message):
    leader_steam_id: int = betterproto.uint64_field(1)
    members: List["AppTeamInfoMember"] = betterproto.message_field(2)
    map_notes: List["AppTeamInfoNote"] = betterproto.message_field(3)
    leader_map_notes: List["AppTeamInfoNote"] = betterproto.message_field(4)


@dataclass
class AppTeamInfoMember(betterproto.Message):
    steam_id: int = betterproto.uint64_field(1)
    name: str = betterproto.string_field(2)
    x: float = betterproto.float_field(3)
    y: float = betterproto.float_field(4)
    is_online: bool = betterproto.bool_field(5)
    spawn_time: int = betterproto.uint32_field(6)
    is_alive: bool = betterproto.bool_field(7)
    death_time: int = betterproto.uint32_field(8)


@dataclass
class AppTeamInfoNote(betterproto.Message):
    type: int = betterproto.int32_field(2)
    x: float = betterproto.float_field(3)
    y: float = betterproto.float_field(4)
    icon: int = betterproto.int32_field(5)
    colour_index: int = betterproto.int32_field(6)
    label: str = betterproto.string_field(7)


@dataclass
class AppTeamMessage(betterproto.Message):
    steam_id: int = betterproto.uint64_field(1)
    name: str = betterproto.string_field(2)
    message: str = betterproto.string_field(3)
    color: str = betterproto.string_field(4)
    time: int = betterproto.uint32_field(5)


@dataclass
class AppTeamChat(betterproto.Message):
    messages: List["AppTeamMessage"] = betterproto.message_field(1)


@dataclass
class AppMarker(betterproto.Message):
    id: int = betterproto.uint32_field(1)
    type: "AppMarkerType" = betterproto.enum_field(2)
    x: float = betterproto.float_field(3)
    y: float = betterproto.float_field(4)
    steam_id: int = betterproto.uint64_field(5)
    rotation: float = betterproto.float_field(6)
    radius: float = betterproto.float_field(7)
    color1: "Vector4" = betterproto.message_field(8)
    color2: "Vector4" = betterproto.message_field(9)
    alpha: float = betterproto.float_field(10)
    name: str = betterproto.string_field(11)
    out_of_stock: bool = betterproto.bool_field(12)
    sell_orders: List["AppMarkerSellOrder"] = betterproto.message_field(13)


@dataclass
class AppMarkerSellOrder(betterproto.Message):
    item_id: int = betterproto.int32_field(1)
    quantity: int = betterproto.int32_field(2)
    currency_id: int = betterproto.int32_field(3)
    cost_per_item: int = betterproto.int32_field(4)
    amount_in_stock: int = betterproto.int32_field(5)
    item_is_blueprint: bool = betterproto.bool_field(6)
    currency_is_blueprint: bool = betterproto.bool_field(7)
    item_condition: float = betterproto.float_field(8)
    item_condition_max: float = betterproto.float_field(9)


@dataclass
class AppMapMarkers(betterproto.Message):
    markers: List["AppMarker"] = betterproto.message_field(1)


@dataclass
class AppClanInfo(betterproto.Message):
    clan_info: "ClanInfo" = betterproto.message_field(1)


@dataclass
class AppClanMessage(betterproto.Message):
    steam_id: int = betterproto.uint64_field(1)
    name: str = betterproto.string_field(2)
    message: str = betterproto.string_field(3)
    time: int = betterproto.int64_field(4)


@dataclass
class AppClanChat(betterproto.Message):
    messages: List["AppClanMessage"] = betterproto.message_field(1)


@dataclass
class AppNexusAuth(betterproto.Message):
    server_id: str = betterproto.string_field(1)
    player_token: int = betterproto.int32_field(2)


@dataclass
class AppTeamChanged(betterproto.Message):
    player_id: int = betterproto.uint64_field(1)
    team_info: "AppTeamInfo" = betterproto.message_field(2)


@dataclass
class AppNewTeamMessage(betterproto.Message):
    message: "AppTeamMessage" = betterproto.message_field(1)


@dataclass
class AppEntityChanged(betterproto.Message):
    entity_id: int = betterproto.uint32_field(1)
    payload: "AppEntityPayload" = betterproto.message_field(2)


@dataclass
class AppClanChanged(betterproto.Message):
    clan_info: "ClanInfo" = betterproto.message_field(1)


@dataclass
class AppNewClanMessage(betterproto.Message):
    clan_id: int = betterproto.int64_field(1)
    message: "AppClanMessage" = betterproto.message_field(2)


@dataclass
class AppCameraSubscribe(betterproto.Message):
    camera_id: str = betterproto.string_field(1)


@dataclass
class AppCameraInput(betterproto.Message):
    buttons: int = betterproto.int32_field(1)
    mouse_delta: "Vector2" = betterproto.message_field(2)


@dataclass
class AppCameraInfo(betterproto.Message):
    width: int = betterproto.int32_field(1)
    height: int = betterproto.int32_field(2)
    near_plane: float = betterproto.float_field(3)
    far_plane: float = betterproto.float_field(4)
    control_flags: int = betterproto.int32_field(5)


@dataclass
class AppCameraRays(betterproto.Message):
    vertical_fov: float = betterproto.float_field(1)
    sample_offset: int = betterproto.int32_field(2)
    ray_data: bytes = betterproto.bytes_field(3)
    distance: float = betterproto.float_field(4)
    entities: List["AppCameraRaysEntity"] = betterproto.message_field(5)
    time_of_day: float = betterproto.float_field(6)


@dataclass
class AppCameraRaysEntity(betterproto.Message):
    entity_id: int = betterproto.uint32_field(1)
    type: "AppCameraRaysEntityType" = betterproto.enum_field(2)
    position: "Vector3" = betterproto.message_field(3)
    rotation: "Vector3" = betterproto.message_field(4)
    size: "Vector3" = betterproto.message_field(5)
    name: str = betterproto.string_field(6)
