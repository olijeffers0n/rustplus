class Error(Exception):
    """Base class for other exceptions"""

    pass


class RateLimitError(Error):
    """Raised When an issue with the ratelimit has occurred"""

    pass


class ServerNotResponsiveError(Error):
    """Raised when the target Server is not online / Unavailable"""

    pass


class CommandsNotEnabledError(Error):
    """Raised when events are not enabled"""

    pass


class ResponseNotReceivedError(Error):
    """Raised when a response has not been received from the server"""

    pass


class PrefixNotDefinedError(Error):
    """Raised when a prefix is not given"""

    pass


class ImageError(Error):
    """Raised when the bytes received are not valid"""

    pass


class ClientNotConnectedError(Error):
    """Raised when you are not connected to the Rust server"""

    pass


class RequestError(Error):
    """Raised when an error is received from the server"""

    pass


class SmartDeviceRegistrationError(Error):
    """Raised when the entity cannot be registered with"""

    pass


class ServerSwitchDisallowedError(Error):
    """Raised when you are using the test server and attempt to swap server"""

    pass
