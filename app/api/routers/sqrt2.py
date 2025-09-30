# app/api/routers/sqrt2.py
"""Square Root of 2 (√2) dedicated endpoints"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional
import time
import random

from app.storage.multi_manager import MultiConstantManager
from app.core.exceptions import CorruptionError
from app.api.models.responses import (
    DigitsResponse, SearchResult, StatsResponse, CacheBuildResponse,
    VerificationResponse, RandomDigitsResponse, ConstantStatusResponse,
    VerificationResult, VerificationFailure
)

router = APIRouter(prefix="/sqrt2", tags=["Square Root of 2 (√2)"])

_storage: Optional[MultiConstantManager] = None

def set_storage(storage: MultiConstantManager):
    global _storage
    _storage = storage

def get_storage():
    if not _storage:
        raise HTTPException(503, "Storage not initialized")
    return _storage

def get_manager():
    return get_storage().get_manager("sqrt2")

@router.get("/status", response_model=ConstantStatusResponse)
async def status():
    """Get √2 status and cache information"""
    return get_storage().get_constant_status("sqrt2")

@router.get("/digits", response_model=DigitsResponse)
async def digits(
    start: int = Query(..., ge=0, description="Starting position (0-based)"),
    length: int = Query(..., ge=1, le=100000, description="Number of digits"),
    verify: bool = Query(False, description="Force verification")
):
    """Retrieve √2 digits from specified position"""
    start_time = time.time()
    manager = get_manager()
    digits = manager.get_digits(start, length, force_verify=verify)
    return DigitsResponse(
        digits=digits,
        start_position=start,
        length=length,
        verified=verify,
        retrieval_time_ms=round((time.time() - start_time) * 1000, 2)
    )

@router.get("/search", response_model=SearchResult)
async def search(
    sequence: str = Query(..., min_length=1, max_length=20, description="Digit sequence to search"),
    max_results: int = Query(100, ge=1, le=1000, description="Maximum results"),
    start_from: int = Query(0, ge=0, description="Start search from position")
):
    """Search for digit sequence in √2"""
    if not sequence.isdigit():
        raise HTTPException(400, "Sequence must contain only digits")
    start_time = time.time()
    manager = get_manager()
    positions = manager.search_sequence(sequence, max_results, start_from)
    return SearchResult(
        sequence=sequence,
        positions=positions,
        total_found=len(positions),
        search_time_ms=round((time.time() - start_time) * 1000, 2)
    )

@router.get("/stats", response_model=StatsResponse)
async def stats(
    start: int = Query(0, ge=0, description="Start position"),
    sample_size: int = Query(100000, ge=1000, le=1000000, description="Sample size")
):
    """Get statistical analysis of √2 digit distribution"""
    start_time = time.time()
    manager = get_manager()
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

@router.get("/random", response_model=RandomDigitsResponse)
async def random_digits(
    length: int = Query(10, ge=1, le=1000, description="Number of digits"),
    seed: Optional[int] = Query(None, description="Random seed")
):
    """Get random digits from √2"""
    if seed is not None:
        random.seed(seed)
    manager = get_manager()
    max_start = manager.get_file_size() - length
    random_start = random.randint(0, max_start)
    digits = manager.get_digits(random_start, length)
    return RandomDigitsResponse(
        digits=digits,
        position=random_start,
        length=length,
        seed_used=seed
    )

@router.post("/build-cache", response_model=CacheBuildResponse)
async def build_cache(
    background_tasks: BackgroundTasks,
    force_rebuild: bool = Query(False, description="Force rebuild existing cache")
):
    """Build SQLite and binary cache for √2"""
    def build_task():
        try:
            get_storage().build_cache("sqrt2", force_rebuild=force_rebuild)
        except Exception as e:
            print(f"❌ Cache build failed: {e}")
    
    background_tasks.add_task(build_task)
    return CacheBuildResponse(
        message="Cache building started for √2",
        status="started",
        estimated_time_minutes=5
    )

@router.post("/verify", response_model=VerificationResponse)
async def verify(
    start: int = Query(0, ge=0, description="Start position"),
    length: int = Query(10000, ge=100, le=100000, description="Segment length"),
    sample_count: int = Query(10, ge=1, le=100, description="Number of samples")
):
    """Verify √2 data integrity across all storage sources"""
    manager = get_manager()
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