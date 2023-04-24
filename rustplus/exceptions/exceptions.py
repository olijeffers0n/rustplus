class Error(Exception):
    """Base class for other exceptions"""



class RateLimitError(Error):
    """Raised When an issue with the ratelimit has occurred"""



class ServerNotResponsiveError(Error):
    """Raised when the target Server is not online / Unavailable"""



class CommandsNotEnabledError(Error):
    """Raised when events are not enabled"""



class ResponseNotReceivedError(Error):
    """Raised when a response has not been received from the server"""



class PrefixNotDefinedError(Error):
    """Raised when a prefix is not given"""



class ImageError(Error):
    """Raised when the bytes received are not valid"""



class ClientNotConnectedError(Error):
    """Raised when you are not connected to the Rust server"""



class RequestError(Error):
    """Raised when an error is received from the server"""



class SmartDeviceRegistrationError(Error):
    """Raised when the entity cannot be registered with"""



class ServerSwitchDisallowedError(Error):
    """Raised when you are using the test server and attempt to swap server"""

