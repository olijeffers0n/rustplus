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

class ResponseNotRecievedError(Error):
    """Raised when a response has not been recieved from the server"""
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