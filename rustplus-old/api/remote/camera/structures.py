from typing import Any

from ..rustplus_proto import AppCameraInfo, AppCameraRaysEntity, AppCameraRays


class CameraInfo:
    def __init__(self, camera_info_message: AppCameraInfo) -> None:
        self.width: int = camera_info_message.width
        self.height: int = camera_info_message.height
        self.near_plane: float = camera_info_message.near_plane
        self.far_plane: float = camera_info_message.far_plane
        self.control_flags: int = camera_info_message.control_flags

    def is_move_option_permissible(self, value: int) -> bool:
        return self.control_flags & value == value

    def __str__(self) -> str:
        return (
            f"CameraInfo(width={self.width}, height={self.height}, near_plane={self.near_plane}, "
            f"far_plane={self.far_plane}, control_flags={self.control_flags})"
        )


class Entity:
    def __init__(self, entity_data: AppCameraRaysEntity) -> None:
        self.entity_id: int = entity_data.entity_id
        self.type: int = entity_data.type
        self.position: Vector3 = Vector3(entity_data.position)
        self.rotation: Vector3 = Vector3(entity_data.rotation)
        self.size: Vector3 = Vector3(entity_data.size)
        self.name: str = entity_data.name

    def __str__(self) -> str:
        return (
            f"Entity(entity_id={self.entity_id}, type={self.type}, position={self.position}, "
            f"rotation={self.rotation}, size={self.size}, name={self.name})"
        )

    def __repr__(self):
        return self.__str__()


class Vector3:
    def __init__(self, vector3=None, x=None, y=None, z=None) -> None:
        self.x: float = vector3.x if x is None else x
        self.y: float = vector3.y if y is None else y
        self.z: float = vector3.z if z is None else z

    def __eq__(self, other):
        if not isinstance(other, Vector3):
            return False

        return self.x == other.x and self.y == other.y and self.z == other.z

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __str__(self) -> str:
        return f"Vector3(x={self.x}, y={self.y}, z={self.z})"


class RayPacket:
    def __init__(self, ray_packet: AppCameraRays) -> None:
        self.vertical_fov = ray_packet.vertical_fov
        self.sample_offset = ray_packet.sample_offset
        self.ray_data = ray_packet.ray_data
        self.distance = ray_packet.distance
        self.entities = [Entity(data) for data in ray_packet.entities]

    def __str__(self) -> str:
        return (
            f"RayPacket(vertical_fov={self.vertical_fov}, sample_offset={self.sample_offset}, "
            f"ray_data={self.ray_data}, distance={self.distance}, entities={self.entities})"
        )


class LimitedQueue:
    def __init__(self, length) -> None:
        self._length = length
        self._queue = []

    def add(self, item) -> None:
        self._queue.append(item)
        if len(self._queue) > self._length:
            self._queue.pop(0)

    def get(self, index=0) -> Any:
        if index >= len(self._queue) or index < 0:
            return None

        return self._queue[index]

    def get_last(self) -> Any:
        return self._queue[-1]

    def pop(self) -> Any:
        return self._queue.pop(0)

    def clear(self) -> None:
        self._queue.clear()

    def __len__(self) -> int:
        return len(self._queue)
