"""
API Response Models

Pydantic models for API responses with proper validation and documentation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class DigitsResponse(BaseModel):
    """Response model for digits retrieval"""
    digits: str = Field(..., description="The requested digits")
    start_position: int = Field(..., description="Starting position (0-based)")
    length: int = Field(..., description="Number of digits returned")
    verified: bool = Field(..., description="Whether the digits were verified")
    retrieval_time_ms: float = Field(..., description="Time taken to retrieve digits in milliseconds")


class SearchResult(BaseModel):
    """Response model for sequence search"""
    sequence: str = Field(..., description="The searched sequence")
    positions: List[int] = Field(..., description="List of positions where sequence was found")
    total_found: int = Field(..., description="Total number of occurrences found")
    search_time_ms: float = Field(..., description="Time taken to search in milliseconds")


class StatsResponse(BaseModel):
    """Response model for statistical analysis"""
    digit_frequencies: Dict[str, float] = Field(..., description="Frequency of each digit as percentage")
    most_common: str = Field(..., description="Most common digit")
    least_common: str = Field(..., description="Least common digit")
    total_digits_analyzed: int = Field(..., description="Total number of digits analyzed")
    analysis_time_ms: float = Field(..., description="Time taken for analysis in milliseconds")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Overall system status")
    sources_available: Dict[str, bool] = Field(..., description="Availability of each storage source")
    last_verification: str = Field(..., description="Timestamp of last verification")


class CacheBuildResponse(BaseModel):
    """Response model for cache building operation"""
    message: str = Field(..., description="Status message")
    status: str = Field(..., description="Operation status")
    estimated_time_minutes: int = Field(..., description="Estimated time to completion in minutes")


class VerificationResult(BaseModel):
    """Individual verification result"""
    position: int = Field(..., description="Position that was verified")
    verified: bool = Field(..., description="Whether verification passed")
    length: int = Field(..., description="Length of verified segment")


class VerificationFailure(BaseModel):
    """Individual verification failure"""
    position: int = Field(..., description="Position where verification failed")
    error: str = Field(..., description="Error message")


class VerificationResponse(BaseModel):
    """Response model for verification operation"""
    status: str = Field(..., description="Overall verification status")
    verifications_completed: int = Field(..., description="Number of verifications completed")
    all_passed: bool = Field(..., description="Whether all verifications passed")
    failed_count: int = Field(..., description="Number of failed verifications")
    results: List[VerificationResult] = Field(..., description="List of verification results")
    failures: List[VerificationFailure] = Field(default=[], description="List of verification failures")


class RandomDigitsResponse(BaseModel):
    """Response model for random digits"""
    digits: str = Field(..., description="The random digits")
    position: int = Field(..., description="Position in the mathematical constant")
    length: int = Field(..., description="Number of digits returned")
    seed_used: Optional[int] = Field(None, description="Seed used for randomness (if any)")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: str = Field(..., description="Error timestamp")


class InfoResponse(BaseModel):
    """General information response"""
    message: str = Field(..., description="Information message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


class ConstantInfo(BaseModel):
    """Information about a mathematical constant"""
    name: str = Field(..., description="Full name of the constant")
    symbol: str = Field(..., description="Mathematical symbol")
    description: str = Field(..., description="Brief description")
    filename: str = Field(..., description="Data filename")
    available: bool = Field(..., description="Whether constant data is available")


class ConstantsListResponse(BaseModel):
    """Response model for listing available constants"""
    constants: List[ConstantInfo] = Field(..., description="List of available mathematical constants")
    total_count: int = Field(..., description="Total number of constants")


class SystemStatsResponse(BaseModel):
    """Response model for system statistics"""
    total_requests: int = Field(..., description="Total number of requests processed")
    cache_hit_rate: float = Field(..., description="Cache hit rate percentage")
    average_response_time_ms: float = Field(..., description="Average response time in milliseconds")
    uptime_seconds: int = Field(..., description="System uptime in seconds")
    file_size_bytes: int = Field(..., description="Size of mathematical constant file in bytes")
    cache_sizes: Dict[str, int] = Field(..., description="Sizes of various caches")


class BulkDigitsRequest(BaseModel):
    """Request model for bulk digits retrieval"""
    requests: List[Dict[str, int]] = Field(..., description="List of start/length pairs")
    verify_all: bool = Field(False, description="Whether to verify all requests")


class BulkDigitsResponse(BaseModel):
    """Response model for bulk digits retrieval"""
    results: List[DigitsResponse] = Field(..., description="List of digit responses")
    total_requests: int = Field(..., description="Total number of requests processed")
    total_time_ms: float = Field(..., description="Total processing time in milliseconds")