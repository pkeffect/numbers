"""
API Request Models

Pydantic models for API requests with proper validation.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional


class DigitsRequest(BaseModel):
    """Request model for digits retrieval"""
    start: int = Field(..., ge=0, description="Starting position (0-based)")
    length: int = Field(..., ge=1, le=100000, description="Number of digits to retrieve")
    verify: bool = Field(False, description="Force verification against original file")
    
    @validator('start')
    def validate_start(cls, v):
        if v < 0:
            raise ValueError('Start position must be non-negative')
        return v
    
    @validator('length')
    def validate_length(cls, v):
        if v < 1 or v > 100000:
            raise ValueError('Length must be between 1 and 100,000')
        return v


class SearchRequest(BaseModel):
    """Request model for sequence search"""
    sequence: str = Field(..., min_length=1, max_length=20, description="Digit sequence to search for")
    max_results: int = Field(100, ge=1, le=1000, description="Maximum number of results")
    start_from: int = Field(0, ge=0, description="Start search from position")
    
    @validator('sequence')
    def validate_sequence(cls, v):
        if not v.isdigit():
            raise ValueError('Sequence must contain only digits')
        if len(v) < 1 or len(v) > 20:
            raise ValueError('Sequence length must be between 1 and 20 digits')
        return v
    
    @validator('max_results')
    def validate_max_results(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Max results must be between 1 and 1,000')
        return v


class StatsRequest(BaseModel):
    """Request model for statistical analysis"""
    start: int = Field(0, ge=0, description="Start position for analysis")
    sample_size: int = Field(100000, ge=1000, le=1000000, description="Number of digits to analyze")
    
    @validator('start')
    def validate_start(cls, v):
        if v < 0:
            raise ValueError('Start position must be non-negative')
        return v
    
    @validator('sample_size')
    def validate_sample_size(cls, v):
        if v < 1000 or v > 1000000:
            raise ValueError('Sample size must be between 1,000 and 1,000,000')
        return v


class RandomDigitsRequest(BaseModel):
    """Request model for random digits"""
    length: int = Field(10, ge=1, le=1000, description="Number of random digits")
    seed: Optional[int] = Field(None, description="Seed for reproducible randomness")
    
    @validator('length')
    def validate_length(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Length must be between 1 and 1,000')
        return v


class VerificationRequest(BaseModel):
    """Request model for verification operation"""
    start: int = Field(0, ge=0, description="Start position for verification")
    length: int = Field(10000, ge=100, le=100000, description="Length of segment to verify")
    sample_count: int = Field(10, ge=1, le=100, description="Number of random samples to verify")
    
    @validator('start')
    def validate_start(cls, v):
        if v < 0:
            raise ValueError('Start position must be non-negative')
        return v
    
    @validator('length')
    def validate_length(cls, v):
        if v < 100 or v > 100000:
            raise ValueError('Length must be between 100 and 100,000')
        return v
    
    @validator('sample_count')
    def validate_sample_count(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Sample count must be between 1 and 100')
        return v


class BulkDigitsRequest(BaseModel):
    """Request model for bulk digits retrieval"""
    requests: List[DigitsRequest] = Field(..., min_items=1, max_items=100, description="List of digit requests")
    verify_all: bool = Field(False, description="Whether to verify all requests")
    
    @validator('requests')
    def validate_requests(cls, v):
        if len(v) < 1 or len(v) > 100:
            raise ValueError('Bulk requests must contain between 1 and 100 individual requests')
        return v


class CacheBuildRequest(BaseModel):
    """Request model for cache building"""
    force_rebuild: bool = Field(False, description="Force rebuild even if cache exists")
    chunk_size_override: Optional[int] = Field(None, ge=1000, le=50000, description="Override default chunk size")
    
    @validator('chunk_size_override')
    def validate_chunk_size(cls, v):
        if v is not None and (v < 1000 or v > 50000):
            raise ValueError('Chunk size must be between 1,000 and 50,000')
        return v


class PatternSearchRequest(BaseModel):
    """Request model for advanced pattern search"""
    pattern: str = Field(..., min_length=1, max_length=50, description="Pattern to search for (can include wildcards)")
    max_results: int = Field(100, ge=1, le=1000, description="Maximum number of results")
    start_from: int = Field(0, ge=0, description="Start search from position")
    use_regex: bool = Field(False, description="Treat pattern as regular expression")
    
    @validator('pattern')
    def validate_pattern(cls, v):
        if len(v) < 1 or len(v) > 50:
            raise ValueError('Pattern length must be between 1 and 50 characters')
        return v


class ConfigUpdateRequest(BaseModel):
    """Request model for configuration updates"""
    chunk_size: Optional[int] = Field(None, ge=1000, le=50000, description="Chunk size for storage")
    verify_every: Optional[int] = Field(None, ge=1, le=1000, description="Verification frequency")
    cache_enabled: Optional[bool] = Field(None, description="Enable/disable caching")
    
    @validator('chunk_size')
    def validate_chunk_size(cls, v):
        if v is not None and (v < 1000 or v > 50000):
            raise ValueError('Chunk size must be between 1,000 and 50,000')
        return v
    
    @validator('verify_every')
    def validate_verify_every(cls, v):
        if v is not None and (v < 1 or v > 1000):
            raise ValueError('Verification frequency must be between 1 and 1,000')
        return v