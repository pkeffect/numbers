"""
Core Module

Core configuration, constants, and exception handling for the math constants system.
"""

from app.core.config import settings
from app.core.constants import MATH_CONSTANTS, KNOWN_PREFIXES
from app.core.exceptions import (
    CorruptionError,
    StorageError,
    ValidationError,
    MathConstantError,
    FileNotFoundError,
    ConfigurationError,
    CacheError,
    VerificationError,
    APIError,
    RateLimitError,
    AuthenticationError,
    AuthorizationError,
)

__all__ = [
    "settings",
    "MATH_CONSTANTS",
    "KNOWN_PREFIXES",
    "CorruptionError",
    "StorageError",
    "ValidationError",
    "MathConstantError",
    "FileNotFoundError",
    "ConfigurationError",
    "CacheError",
    "VerificationError",
    "APIError",
    "RateLimitError",
    "AuthenticationError",
    "AuthorizationError",
]