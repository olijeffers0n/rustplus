class Error(Exception):
    """Base class for other exceptions"""
    pass

class ClientError(Error):
    """Raised when the client details are not valid"""
    pass

class ImageError(Error):
    """Raised when the Returned Image Bytes are not valid"""
    pass

class ServerNotResponsiveError(Error):
    """Raised when the target Server is not online / Unavailable"""
    pass

class ClientNotConnectedError(Error):
    """Raised when the client is not connected to the server"""
    pass

class PrefixNotDefinedError(Error):
    """Raised when a prefix is not given"""
    pass

class EventsNotEnabledError(Error):
    """Raised when events are not enabled"""
    pass