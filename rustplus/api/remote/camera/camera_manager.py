from ..rustplus_proto import AppCameraRays, AppCameraInfo


class CameraManager:

    def __init__(self, rust_socket, cam_id, cam_info_message) -> None:
        self.rust_socket = rust_socket
        self._cam_id = cam_id
        self._last_packet: AppCameraRays = None
        self._cam_info_message: AppCameraInfo = cam_info_message

    def set_packet(self, packet):
        self._last_packet = packet

    def get_frame(self):
        if self._last_packet is None:
            return None

        return self._last_packet
