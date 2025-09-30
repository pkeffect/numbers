# app/api/routers/legacy.py
"""
Legacy parameterized endpoints for backward compatibility.
These redirect to the new dedicated endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Path
from typing import Optional
import time
import random

from app.storage.multi_manager import MultiConstantManager
from app.core.exceptions import CorruptionError
from app.api.models.responses import (
    DigitsResponse, SearchResult, StatsResponse,
    RandomDigitsResponse, CacheBuildResponse,
    VerificationResponse, VerificationResult, VerificationFailure
)

router = APIRouter(tags=["Legacy (Deprecated)"], deprecated=True)

_storage: Optional[MultiConstantManager] = None

def set_storage(storage: MultiConstantManager):
    global _storage
    _storage = storage

def get_storage():
    if not _storage:
        raise HTTPException(503, "Storage not initialized")
    return _storage

def validate_constant(constant_id: str):
    storage = get_storage()
    if not storage.has_constant(constant_id):
        available = storage.get_available_constants()
        raise HTTPException(
            404,
            f"'{constant_id}' not available. Available: {', '.join(available)}"
        )

@router.get("/digits/{constant_id}", response_model=DigitsResponse, deprecated=True)
async def get_digits_legacy(
    constant_id: str = Path(..., description="Mathematical constant ID"),
    start: int = Query(..., ge=0),
    length: int = Query(..., ge=1, le=100000),
    verify: bool = Query(False)
):
    """
    DEPRECATED: Use /{constant}/digits instead
    
    Retrieve digits from specified mathematical constant.
    """
    validate_constant(constant_id)
    start_time = time.time()
    manager = get_storage().get_manager(constant_id)
    digits = manager.get_digits(start, length, force_verify=verify)
    return DigitsResponse(
        digits=digits,
        start_position=start,
        length=length,
        verified=verify,
        retrieval_time_ms=round((time.time() - start_time) * 1000, 2)
    )

@router.get("/search/{constant_id}", response_model=SearchResult, deprecated=True)
async def search_sequence_legacy(
    constant_id: str = Path(...),
    sequence: str = Query(..., min_length=1, max_length=20),
    max_results: int = Query(100, ge=1, le=1000),
    start_from: int = Query(0, ge=0)
):
    """DEPRECATED: Use /{constant}/search instead"""
    validate_constant(constant_id)
    if not sequence.isdigit():
        raise HTTPException(400, "Sequence must contain only digits")
    start_time = time.time()
    manager = get_storage().get_manager(constant_id)
    positions = manager.search_sequence(sequence, max_results, start_from)
    return SearchResult(
        sequence=sequence,
        positions=positions,
        total_found=len(positions),
        search_time_ms=round((time.time() - start_time) * 1000, 2)
    )

@router.get("/stats/{constant_id}", response_model=StatsResponse, deprecated=True)
async def get_statistics_legacy(
    constant_id: str = Path(...),
    start: int = Query(0, ge=0),
    sample_size: int = Query(100000, ge=1000, le=1000000)
):
    """DEPRECATED: Use /{constant}/stats instead"""
    validate_constant(constant_id)
    start_time = time.time()
    manager = get_storage().get_manager(constant_id)
    digits = manager.get_digits(start, sample_size)
    
    frequencies = {str(i): 0 for i in range(10)}
    for digit in digits:
        if digit.isdigit():
            frequencies[digit] += 1
    
    total = sum(frequencies.values())
    if total == 0:
        raise ValueError("No digits in sample")
    
    percentages = {d: (c / total) * 100 for d, c in frequencies.items()}
    most_common = max(percentages, key=percentages.get)
    least_common = min(percentages, key=percentages.get)
    
    return StatsResponse(
        digit_frequencies=percentages,
        most_common=most_common,
        least_common=least_common,
        total_digits_analyzed=total,
        analysis_time_ms=round((time.time() - start_time) * 1000, 2)
    )

@router.get("/random/{constant_id}", response_model=RandomDigitsResponse, deprecated=True)
async def get_random_digits_legacy(
    constant_id: str = Path(...),
    length: int = Query(10, ge=1, le=1000),
    seed: Optional[int] = Query(None)
):
    """DEPRECATED: Use /{constant}/random instead"""
    validate_constant(constant_id)
    if seed is not None:
        random.seed(seed)
    manager = get_storage().get_manager(constant_id)
    max_start = manager.get_file_size() - length
    random_start = random.randint(0, max_start)
    digits = manager.get_digits(random_start, length)
    return RandomDigitsResponse(
        digits=digits,
        position=random_start,
        length=length,
        seed_used=seed
    )

@router.post("/admin/build-cache/{constant_id}", response_model=CacheBuildResponse, deprecated=True)
async def build_cache_legacy(
    background_tasks: BackgroundTasks,
    constant_id: str = Path(...),
    force_rebuild: bool = Query(False)
):
    """DEPRECATED: Use /{constant}/build-cache instead"""
    validate_constant(constant_id)
    
    def build_task():
        try:
            get_storage().build_cache(constant_id, force_rebuild=force_rebuild)
        except Exception as e:
            print(f"❌ Cache build failed: {e}")
    
    background_tasks.add_task(build_task)
    
    from app.core.constants import MATH_CONSTANTS
    constant_info = MATH_CONSTANTS[constant_id]
    return CacheBuildResponse(
        message=f"Cache building started for {constant_info.name} ({constant_info.symbol})",
        status="started",
        estimated_time_minutes=5
    )

@router.post("/admin/verify/{constant_id}", response_model=VerificationResponse, deprecated=True)
async def verify_integrity_legacy(
    constant_id: str = Path(...),
    start: int = Query(0, ge=0),
    length: int = Query(10000, ge=100, le=100000),
    sample_count: int = Query(10, ge=1, le=100)
):
    """DEPRECATED: Use /{constant}/verify instead"""
    validate_constant(constant_id)
    
    manager = get_storage().get_manager(constant_id)
    verification_results = []
    failed_verifications = []
    
    for _ in range(sample_count):
        pos = random.randint(start, start + length - 100)
        try:
            manager.get_digits(pos, 100, force_verify=True)
            verification_results.append({
                "position": pos,
                "verified": True,
                "length": 100
            })
        except CorruptionError as e:
            failed_verifications.append({
                "position": pos,
                "error": str(e)
            })
    
    return VerificationResponse(
        status="success" if not failed_verifications else "partial_failure",
        verifications_completed=len(verification_results),
        all_passed=len(failed_verifications) == 0,
        failed_count=len(failed_verifications),
        results=[VerificationResult(**r) for r in verification_results],
        failures=[VerificationFailure(**f) for f in failed_verifications]
    )