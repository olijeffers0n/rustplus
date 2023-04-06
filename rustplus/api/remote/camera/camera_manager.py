import time
import traceback
from typing import Iterable, Union, List, Coroutine

from PIL import Image

from .camera_parser import Parser
from ..events import EventLoopManager, EventHandler
from ..rustplus_proto import AppCameraInput, Vector2, AppEmpty
from ...structures import Vector
from .structures import CameraInfo, LimitedQueue, Entity


class CameraManager:
    def __init__(self, rust_socket, cam_id, cam_info_message) -> None:
        self.rust_socket = rust_socket
        self._cam_id = cam_id
        self._last_packets: LimitedQueue = LimitedQueue(6)
        self._cam_info_message: CameraInfo = CameraInfo(cam_info_message)
        self._open = True
        self.parser = Parser(
            self._cam_info_message.width, self._cam_info_message.height
        )
        self.time_since_last_subscribe = time.time()
        self.frame_callbacks = set()

    def add_packet(self, packet) -> None:
        self._last_packets.add(packet)

        if len(self.frame_callbacks) == 0:
            return

        try:
            frame = self._create_frame()
        except Exception:
            traceback.print_exc()
            return

        for callback in self.frame_callbacks:
            EventHandler.schedule_event(
                EventLoopManager.get_loop(self.rust_socket.server_id),
                callback,
                frame,
            )

    def on_frame_received(self, coro) -> Coroutine:
        self.frame_callbacks.add(coro)
        return coro

    def has_frame_data(self) -> bool:
        return len(self._last_packets) > 0

    def _create_frame(self) -> Union[Image.Image, None]:
        if self._last_packets is None:
            return None

        if not self._open:
            raise Exception("Camera is closed")

        for i in range(len(self._last_packets)):
            self.parser.handle_camera_ray_data(self._last_packets.get(i))
            self.parser.step()

        last_packet = self._last_packets.get_last()

        return self.parser.render(last_packet.entities, last_packet.vertical_fov, self._cam_info_message.far_plane)

    async def get_frame(self) -> Union[Image.Image, None]:
        return self._create_frame()

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
        app_request = self.rust_socket._generate_protobuf()
        cam_input = AppCameraInput()

        cam_input.buttons = value
        vector = Vector2()
        vector.x = joystick_vector.x
        vector.y = joystick_vector.y
        cam_input.mouseDelta.CopyFrom(vector)
        app_request.cameraInput.CopyFrom(cam_input)

        await self.rust_socket.remote.send_message(app_request)
        self.rust_socket.remote.ignored_responses.append(app_request.seq)

    async def exit_camera(self) -> None:
        await self.rust_socket._handle_ratelimit()
        app_request = self.rust_socket._generate_protobuf()
        app_request.cameraUnsubscribe.CopyFrom(AppEmpty())

        await self.rust_socket.remote.send_message(app_request)
        self.rust_socket.remote.ignored_responses.append(app_request.seq)

        self._open = False
        self._last_packets.clear()

    async def resubscribe(self) -> None:
        await self.rust_socket.remote.subscribe_to_camera(self._cam_id, True)
        self.time_since_last_subscribe = time.time()
        self._open = True
        self._last_packets.clear()
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
