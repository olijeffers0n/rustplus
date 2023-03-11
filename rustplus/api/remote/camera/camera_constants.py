class MovementControls:
    """
    Possible inputs for the camera movement.
    """

    FORWARD = 2
    BACKWARD = 4
    LEFT = 8
    RIGHT = 16
    JUMP = 32
    DUCK = 64
    SPRINT = 128
    USE = 256
    FIRE_PRIMARY = 1024
    FIRE_SECONDARY = 2048
    RELOAD = 8192
    FIRE_THIRD = 134217728


class CameraMovementOptions:
    """
    Indicate which camera controls are active for the camera.

    """
    NONE = 0
    MOVEMENT = 1
    MOUSE = 2
    SPRINT_AND_DUCK = 4
    FIRE = 8
    RELOAD = 16
    CROSSHAIR = 32