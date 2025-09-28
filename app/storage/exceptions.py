"""
Custom exceptions for the Math Constants Storage System.
"""

from typing import Optional, Any


class MathConstantError(Exception):
    """Base exception for math constants system."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class StorageError(MathConstantError):
    """Exception raised for storage-related errors."""
    pass


class CorruptionError(StorageError):
    """Exception raised when data corruption is detected."""
    
    def __init__(self, message: str, position: Optional[int] = None, 
                 source: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message, details)
        self.position = position
        self.source = source


class ValidationError(MathConstantError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, details: Optional[dict] = None):
        super().__init__(message, details)
        self.field = field
        self.value = value


class FileNotFoundError(StorageError):
    """Exception raised when a required file is not found."""
    
    def __init__(self, filepath: str, details: Optional[dict] = None):
        message = f"Required file not found: {filepath}"
        super().__init__(message, details)
        self.filepath = filepath


class ConfigurationError(MathConstantError):
    """Exception raised for configuration-related errors."""
    pass


class CacheError(StorageError):
    """Exception raised for cache-related errors."""
    pass


class VerificationError(CorruptionError):
    """Exception raised when verification fails."""
    pass


class APIError(MathConstantError):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, status_code: int = 500, 
                 details: Optional[dict] = None):
        super().__init__(message, details)
        self.status_code = status_code


class RateLimitError(APIError):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None, details: Optional[dict] = None):
        super().__init__(message, 429, details)
        self.retry_after = retry_after


class AuthenticationError(APIError):
    """Exception raised for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed", 
                 details: Optional[dict] = None):
        super().__init__(message, 401, details)


class AuthorizationError(APIError):
    """Exception raised for authorization errors."""
    
    def __init__(self, message: str = "Access denied", 
                 details: Optional[dict] = None):
        super().__init__(message, 403, details)"""
Custom exceptions for the Math Constants Storage System.
"""

from typing import Optional, Any


class MathConstantError(Exception):
    """Base exception for math constants system."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class StorageError(MathConstantError):
    """Exception raised for storage-related errors."""
    pass


class CorruptionError(StorageError):
    """Exception raised when data corruption is detected."""
    
    def __init__(self, message: str, position: Optional[int] = None, 
                 source: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message, details)
        self.position = position
        self.source = source


class ValidationError(MathConstantError):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 value: Optional[Any] = None, details: Optional[dict] = None):
        super().__init__(message, details)
        self.field = field
        self.value = value


class FileNotFoundError(StorageError):
    """Exception raised when a required file is not found."""
    
    def __init__(self, filepath: str, details: Optional[dict] = None):
        message = f"Required file not found: {filepath}"
        super().__init__(message, details)
        self.filepath = filepath


class ConfigurationError(MathConstantError):
    """Exception raised for configuration-related errors."""
    pass


class CacheError(StorageError):
    """Exception raised for cache-related errors."""
    pass


class VerificationError(CorruptionError):
    """Exception raised when verification fails."""
    pass


class APIError(MathConstantError):
    """Exception raised for API-related errors."""
    
    def __init__(self, message: str, status_code: int = 500, 
                 details: Optional[dict] = None):
        super().__init__(message, details)
        self.status_code = status_code


class RateLimitError(APIError):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", 
                 retry_after: Optional[int] = None, details: Optional[dict] = None):
        super().__init__(message, 429, details)
        self.retry_after = retry_after


class AuthenticationError(APIError):
    """Exception raised for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed", 
                 details: Optional[dict] = None):
        super().__init__(message, 401, details)


class AuthorizationError(APIError):
    """Exception raised for authorization errors."""
    
    def __init__(self, message: str = "Access denied", 
                 details: Optional[dict] = None):
        super().__init__(message, 403, details)