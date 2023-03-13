class CameraInfo:

    def __init__(self, camera_info_message) -> None:
        self.width = camera_info_message.width
        self.height = camera_info_message.height
        self.near_plane = camera_info_message.nearPlane
        self.far_plane = camera_info_message.farPlane
        self.control_flags = camera_info_message.controlFlags

    def is_move_option_permissible(self, value: int) -> bool:
        return self.control_flags & value == value

    def __str__(self):
        return f"CameraInfo(width={self.width}, height={self.height}, near_plane={self.near_plane}, " \
               f"far_plane={self.far_plane}, control_flags={self.control_flags})"


class Entity:

    def __init__(self, entity_data) -> None:
        self.entity_id = entity_data.entityId
        self.type = entity_data.type
        self.position = entity_data.position
        self.rotation = entity_data.rotation
        self.size = entity_data.size
        self.name = entity_data.name

    def __str__(self):
        return f"Entity(entity_id={self.entity_id}, type={self.type}, position={self.position}, " \
               f"rotation={self.rotation}, size={self.size}, name={self.name})"


class RayPacket:

    def __init__(self, ray_packet) -> None:
        self.vertical_fov = ray_packet.verticalFov
        self.sample_offset = ray_packet.sampleOffset
        self.ray_data = ray_packet.rayData
        self.distance = ray_packet.distance
        self.entities = [Entity(data) for data in ray_packet.entities]

    def __str__(self):
        return f"RayPacket(vertical_fov={self.vertical_fov}, sample_offset={self.sample_offset}, " \
               f"ray_data={self.ray_data}, distance={self.distance}, entities={self.entities})"


class LimitedQueue:

    def __init__(self, length) -> None:
        self._length = length
        self._queue = []

    def add(self, item):
        self._queue.append(item)
        if len(self._queue) > self._length:
            self._queue.pop(0)

    def get(self, index=0):
        return self._queue[index]

    def pop(self):
        return self._queue.pop(0)

    def __len__(self):
        return len(self._queue)
