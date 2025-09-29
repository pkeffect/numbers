"""
API Models

Pydantic models for request and response validation.
"""

from app.api.models.requests import (
    DigitsRequest,
    SearchRequest,
    StatsRequest,
    RandomDigitsRequest,
    VerificationRequest,
    BulkDigitsRequest,
    CacheBuildRequest,
    PatternSearchRequest,
    ConfigUpdateRequest,
)

from app.api.models.responses import (
    DigitsResponse,
    SearchResult,
    StatsResponse,
    HealthResponse,
    CacheBuildResponse,
    VerificationResponse,
    RandomDigitsResponse,
    ErrorResponse,
    InfoResponse,
    ConstantInfo,
    ConstantsListResponse,
    SystemStatsResponse,
    BulkDigitsResponse,
)

__all__ = [
    # Request models
    "DigitsRequest",
    "SearchRequest",
    "StatsRequest",
    "RandomDigitsRequest",
    "VerificationRequest",
    "BulkDigitsRequest",
    "CacheBuildRequest",
    "PatternSearchRequest",
    "ConfigUpdateRequest",
    # Response models
    "DigitsResponse",
    "SearchResult",
    "StatsResponse",
    "HealthResponse",
    "CacheBuildResponse",
    "VerificationResponse",
    "RandomDigitsResponse",
    "ErrorResponse",
    "InfoResponse",
    "ConstantInfo",
    "ConstantsListResponse",
    "SystemStatsResponse",
    "BulkDigitsResponse",
]