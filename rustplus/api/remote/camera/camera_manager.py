from typing import Iterable
from ..rustplus_proto import AppCameraInput, Vector2, AppEmpty
from ...structures import Vector
from .structures import CameraInfo, RayPacket


class CameraManager:

    def __init__(self, rust_socket, cam_id, cam_info_message) -> None:
        self.rust_socket = rust_socket
        self._cam_id = cam_id
        self._last_packet: RayPacket = None
        self._cam_info_message: CameraInfo = CameraInfo(cam_info_message)
        self._open = True

    def set_packet(self, packet):
        self._last_packet = packet

    def has_packet(self) -> bool:
        return self._last_packet is not None

    def get_frame(self):
        if self._last_packet is None:
            return None

        if not self._open:
            raise Exception("Camera is closed")

        return self._last_packet

    def can_move(self, control_type: int) -> bool:
        return self._cam_info_message.is_move_option_permissible(control_type)

    async def clear_movement(self) -> None:
        await self.send_combined_movement()

    async def send_actions(self, actions: Iterable[int]) -> None:
        await self.send_combined_movement(actions)

    async def send_mouse_movement(self, mouse_delta: Vector) -> None:
        await self.send_combined_movement(joystick_vector=mouse_delta)

    async def send_combined_movement(self, movements: Iterable[int] = None, joystick_vector: Vector = None) -> None:

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
        self._last_packet = None
