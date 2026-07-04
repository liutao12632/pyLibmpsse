class PlatformError(Exception):
    """Base class for all platform-related errors."""
    pass

class DLLLoadError(PlatformError):
    """Raised when a DLL fails to load."""
    pass