import time
from typing import Iterable, Union, List, Coroutine, TypeVar, Set, Callable

from PIL import Image

from .camera_parser import Parser
from ..rustplus_proto import (
    AppCameraInput,
    Vector2,
    AppEmpty,
    AppRequest,
    AppCameraInfo,
)
from ...structures import Vector
from .structures import CameraInfo, Entity, LimitedQueue

RS = TypeVar("RS", bound="RustSocket")


class CameraManager:
    def __init__(
        self, rust_socket: RS, cam_id: str, cam_info_message: AppCameraInfo
    ) -> None:
        self.rust_socket: RS = rust_socket
        self._cam_id: str = cam_id
        self._last_packets: LimitedQueue = LimitedQueue(6)
        self._cam_info_message: CameraInfo = CameraInfo(cam_info_message)
        self._open: bool = True
        self.parser: Parser = Parser(
            self._cam_info_message.width, self._cam_info_message.height
        )
        self.time_since_last_subscribe: float = time.time()
        self.frame_callbacks: Set[Callable[[Image.Image], Coroutine]] = set()

    async def add_packet(self, packet) -> None:
        self._last_packets.add(packet)

        if len(self.frame_callbacks) == 0:
            return

        frame = await self._create_frame()

        for callback in self.frame_callbacks:
            await callback(frame)

    def on_frame_received(
        self, coro: Callable[[Image.Image], Coroutine]
    ) -> Callable[[Image.Image], Coroutine]:
        self.frame_callbacks.add(coro)
        return coro

    def has_frame_data(self) -> bool:
        return self._last_packets is not None and len(self._last_packets) > 0

    async def _create_frame(
        self,
        render_entities: bool = True,
        entity_render_distance: float = float("inf"),
        max_entity_amount: int = float("inf"),
    ) -> Union[Image.Image, None]:
        if self._last_packets is None:
            return None

        if len(self._last_packets) == 0:
            return None

        if not self._open:
            raise Exception("Camera is closed")

        for i in range(len(self._last_packets)):
            self.parser.handle_camera_ray_data(self._last_packets.get(i))
            self.parser.step()

        last_packet = self._last_packets.get_last()

        self._last_packets.clear()
        self._last_packets.add(last_packet)

        return self.parser.render(
            render_entities,
            last_packet.entities,
            last_packet.vertical_fov,
            self._cam_info_message.far_plane,
            entity_render_distance,
            max_entity_amount
            if max_entity_amount is not None
            else len(self._last_packets.get_last().entities),
        )

    async def get_frame(
        self,
        render_entities: bool = True,
        entity_render_distance: float = float("inf"),
        max_entity_amount: int = float("inf"),
    ) -> Union[Image.Image, None]:
        return await self._create_frame(
            render_entities, entity_render_distance, max_entity_amount
        )

    def can_move(self, control_type: int) -> bool:
        return self._cam_info_message.is_move_option_permissible(control_type)

    async def clear_movement(self) -> None:
        await self.send_combined_movement()

    async def send_actions(self, actions: Iterable[int]) -> None:
        await self.send_combined_movement(actions)

    async def send_mouse_movement(self, mouse_delta: Vector) -> None:
        await self.send_combined_movement(joystick_vector=mouse_delta)

    async def send_combined_movement(
        self, movements: Iterable[int] = None, joystick_vector: Vector = None
    ) -> None:
        if joystick_vector is None:
            joystick_vector = Vector()

        if movements is None:
            movements = []

        value = 0
        for movement in movements:
            value = value | movement

        await self.rust_socket._handle_ratelimit(0.01)
        app_request: AppRequest = self.rust_socket._generate_protobuf()
        cam_input = AppCameraInput()

        cam_input.buttons = value
        vector = Vector2()
        vector.x = joystick_vector.x
        vector.y = joystick_vector.y
        cam_input.mouse_delta = vector
        app_request.camera_input = cam_input

        await self.rust_socket.remote.send_message(app_request)
        await self.rust_socket.remote.add_ignored_response(app_request.seq)

    async def exit_camera(self) -> None:
        await self.rust_socket._handle_ratelimit()
        app_request: AppRequest = self.rust_socket._generate_protobuf()
        app_request.camera_unsubscribe = AppEmpty()
        app_request.camera_unsubscribe._serialized_on_wire = True

        await self.rust_socket.remote.send_message(app_request)
        await self.rust_socket.remote.add_ignored_response(app_request.seq)

        self._open = False
        self._last_packets.clear()

    async def resubscribe(self) -> None:
        await self.rust_socket.remote.subscribe_to_camera(self._cam_id, True)
        self.time_since_last_subscribe = time.time()
        self._open = True
        self.rust_socket.remote.camera_manager = self

    async def get_entities_in_frame(self) -> List[Entity]:
        if self._last_packets is None:
            return []

        if len(self._last_packets) == 0:
            return []

        return self._last_packets.get_last().entities

    async def get_distance_from_player(self) -> float:
        if self._last_packets is None:
            return float("inf")

        if len(self._last_packets) == 0:
            return float("inf")

        return self._last_packets.get_last().distance

    async def get_max_distance(self) -> float:
        return self._cam_info_message.far_plane
