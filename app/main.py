# app/main.py
"""
Math Constants Storage System - Main Application

Multi-constant API with smart cache management and triple-redundancy storage.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import time
from contextlib import asynccontextmanager

# Import storage system
from app.storage.multi_manager import MultiConstantManager
from app.core.exceptions import CorruptionError, StorageError
from app.core.constants import MATH_CONSTANTS

# Import API models
from app.api.models.responses import (
    DigitsResponse,
    SearchResult,
    StatsResponse,
    MultiConstantHealthResponse,
    CacheBuildResponse,
    BulkCacheBuildResponse,
    VerificationResponse,
    RandomDigitsResponse,
    ConstantInfo,
    ConstantsListResponse,
    ConstantStatusResponse,
)
from app.core.config import settings

# Global storage instance
multi_storage: Optional[MultiConstantManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize storage on startup and cleanup on shutdown"""
    global multi_storage
    
    try:
        print("🔧 Initializing Math Constants Multi-Storage System...")
        multi_storage = MultiConstantManager()
        
        available = multi_storage.get_available_constants()
        print(f"✅ Multi-constant storage system initialized successfully")
        print(f"📊 Available constants: {len(available)}")
        
        # Show cache status summary
        cached_count = sum(1 for cid in available if multi_storage.get_manager(cid).has_sqlite_cache())
        print(f"💾 Cached constants: {cached_count}/{len(available)}")
        
        yield
        
    except Exception as e:
        print(f"❌ Failed to initialize multi-storage: {e}")
        print("⚠️  System will start but endpoints will return 503 errors")
        yield
        
    finally:
        print("🛑 Shutting down multi-storage system")
        if multi_storage:
            multi_storage.cleanup()

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description + " - Multi-Constant Support",
    version=settings.api_version,
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# ============================================================================
# HEALTH AND STATUS ENDPOINTS
# ============================================================================

@app.get("/health", response_model=MultiConstantHealthResponse)
async def health_check():
    """Check system health and storage integrity across all constants"""
    print("❤️  Health check requested")
    
    if not multi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    try:
        available = multi_storage.get_available_constants()
        if not available:
            raise HTTPException(status_code=503, detail="No mathematical constants available")
        
        # Test basic functionality with first available constant
        test_constant = available[0]
        manager = multi_storage.get_manager(test_constant)
        test_digits = manager.get_digits(0, 10, force_verify=True)
        test_passed = len(test_digits) == 10
        
        # Build cache status for each constant
        constants_status = {}
        cached_count = 0
        for constant_id in available:
            mgr = multi_storage.get_manager(constant_id)
            has_cache = mgr.has_sqlite_cache()
            constants_status[constant_id] = has_cache
            if has_cache:
                cached_count += 1
        
        # Determine overall status
        if test_passed and cached_count == len(available):
            status = "healthy"
        elif test_passed and cached_count > 0:
            status = "degraded"
        else:
            status = "unhealthy"
        
        print(f"✅ Health check passed - Status: {status}")
        
        return MultiConstantHealthResponse(
            status=status,
            total_constants=len(available),
            cached_constants=cached_count,
            constants_status=constants_status,
            available_constants=available,
            last_verification=time.strftime("%Y-%m-%d %H:%M:%S"),
            test_passed=test_passed
        )
        
    except Exception as e:
        print(f"💥 Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/constants", response_model=ConstantsListResponse)
async def list_constants():
    """List all mathematical constants with their availability status"""
    if not multi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    statuses = multi_storage.get_all_statuses()
    available_ids = multi_storage.get_available_constants()
    
    constants_info = []
    available_count = 0
    cached_count = 0
    
    for constant_id, status in statuses.items():
        is_available = constant_id in available_ids
        is_cached = False
        
        if is_available:
            available_count += 1
            is_cached = multi_storage.get_manager(constant_id).has_sqlite_cache()
            if is_cached:
                cached_count += 1
        
        constants_info.append(ConstantInfo(
            constant_id=constant_id,
            name=status.name,
            symbol=status.symbol,
            description=MATH_CONSTANTS[constant_id].description,
            filename=MATH_CONSTANTS[constant_id].filename,
            available=is_available,
            file_exists=status.file_exists,
            cached=is_cached
        ))
    
    return ConstantsListResponse(
        constants=constants_info,
        total_count=len(constants_info),
        available_count=available_count,
        cached_count=cached_count
    )


@app.get("/constants/{constant_id}/status", response_model=ConstantStatusResponse)
async def get_constant_status(
    constant_id: str = Path(..., description="Mathematical constant ID (e.g., 'pi', 'e', 'phi')")
):
    """Get detailed status for a specific mathematical constant"""
    if not multi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    try:
        status = multi_storage.get_constant_status(constant_id)
        is_available = multi_storage.has_constant(constant_id)
        
        return ConstantStatusResponse(
            constant_id=constant_id,
            name=status.name,
            symbol=status.symbol,
            file_exists=status.file_exists,
            file_path=status.file_path,
            file_size_bytes=status.file_size,
            cache_exists=status.cache_exists,
            cache_complete=status.cache_complete,
            cached_digits=status.cached_digits,
            available=is_available
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DIGIT RETRIEVAL ENDPOINTS
# ============================================================================

@app.get("/digits/{constant_id}", response_model=DigitsResponse)
async def get_digits(
    constant_id: str = Path(..., description="Mathematical constant ID (e.g., 'pi', 'e', 'phi')"),
    start: int = Query(..., ge=0, description="Starting position (0-based)"),
    length: int = Query(..., ge=1, le=100000, description="Number of digits to retrieve"),
    verify: bool = Query(False, description="Force verification against original file")
):
    """Retrieve digits from specified mathematical constant with optional verification"""
    if not multi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    if not multi_storage.has_constant(constant_id):
        available = multi_storage.get_available_constants()
        raise HTTPException(
            status_code=404, 
            detail=f"Mathematical constant '{constant_id}' not available. Available: {', '.join(available)}"
        )
    
    start_time = time.time()
    
    try:
        manager = multi_storage.get_manager(constant_id)
        digits = manager.get_digits(start, length, force_verify=verify)
        retrieval_time = (time.time() - start_time) * 1000
        
        return DigitsResponse(
            digits=digits,
            start_position=start,
            length=length,
            verified=verify,
            retrieval_time_ms=round(retrieval_time, 2)
        )
        
    except CorruptionError as e:
        raise HTTPException(status_code=500, detail=f"Data corruption detected: {str(e)}")
    except StorageError as e:
        raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/random/{constant_id}", response_model=RandomDigitsResponse)
async def get_random_digits(
    constant_id: str = Path(..., description="Mathematical constant ID"),
    length: int = Query(10, ge=1, le=1000, description="Number of random digits"),
    seed: Optional[int] = Query(None, description="Seed for reproducible randomness")
):
    """Get 'random' digits from a random position in the mathematical constant"""
    if not multi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    if not multi_storage.has_constant(constant_id):
        raise HTTPException(status_code=404, detail=f"Mathematical constant '{constant_id}' not available")
    
    import random
    
    if seed is not None:
        random.seed(seed)
    
    try:
        manager = multi_storage.get_manager(constant_id)
        max_start = manager.get_file_size() - length
        if max_start < 0:
            raise ValueError(f"Requested length {length} exceeds file size")
        
        random_start = random.randint(0, max_start)
        digits = manager.get_digits(random_start, length)
        
        return RandomDigitsResponse(
            digits=digits,
            position=random_start,
            length=length,
            seed_used=seed
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SEARCH AND ANALYSIS ENDPOINTS
# ============================================================================

@app.get("/search/{constant_id}", response_model=SearchResult)
async def search_sequence(
    constant_id: str = Path(..., description="Mathematical constant ID"),
    sequence: str = Query(..., min_length=1, max_length=20, description="Digit sequence to search for"),
    max_results: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    start_from: int = Query(0, ge=0, description="Start search from position")
):
    """Search for a specific digit sequence in a mathematical constant"""
    if not multi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    if not multi_storage.has_constant(constant_id):
        raise HTTPException(status_code=404, detail=f"Mathematical constant '{constant_id}' not available")
    
    if not sequence.isdigit():
        raise HTTPException(status_code=400, detail="Sequence must contain only digits")
    
    start_time = time.time()
    
    try:
        manager = multi_storage.get_manager(constant_id)
        positions = manager.search_sequence(sequence, max_results, start_from)
        search_time = (time.time() - start_time) * 1000
        
        return SearchResult(
            sequence=sequence,
            positions=positions,
            total_found=len(positions),
            search_time_ms=round(search_time, 2)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/stats/{constant_id}", response_model=StatsResponse)
async def get_statistics(
    constant_id: str = Path(..., description="Mathematical constant ID"),
    start: int = Query(0, ge=0, description="Start position for analysis"),
    sample_size: int = Query(100000, ge=1000, le=1000000, description="Number of digits to analyze")
):
    """Get statistical analysis of digit distribution in a mathematical constant"""
    if not multi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    if not multi_storage.has_constant(constant_id):
        raise HTTPException(status_code=404, detail=f"Mathematical constant '{constant_id}' not available")
    
    start_time = time.time()
    
    try:
        manager = multi_storage.get_manager(constant_id)
        digits = manager.get_digits(start, sample_size)
        
        # Count digit frequencies
        frequencies = {str(i): 0 for i in range(10)}
        for digit in digits:
            if digit.isdigit():
                frequencies[digit] += 1
        
        # Convert to percentages
        total_digits = sum(frequencies.values())
        if total_digits == 0:
            raise ValueError("No digits found in sample")
        
        percentages = {digit: (count / total_digits) * 100 
                      for digit, count in frequencies.items()}
        
        most_common = max(percentages, key=percentages.get)
        least_common = min(percentages, key=percentages.get)
        
        analysis_time = (time.time() - start_time) * 1000
        
        return StatsResponse(
            digit_frequencies=percentages,
            most_common=most_common,
            least_common=least_common,
            total_digits_analyzed=total_digits,
            analysis_time_ms=round(analysis_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistical analysis failed: {str(e)}")


# ============================================================================
# ADMIN / CACHE MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/admin/build-cache/{constant_id}", response_model=CacheBuildResponse)
async def build_cache(
    background_tasks: BackgroundTasks,
    constant_id: str = Path(..., description="Mathematical constant ID"),
    force_rebuild: bool = Query(False, description="Force rebuild even if cache exists")
):
    """Build cache for a specific mathematical constant (runs in background)"""
    if not multi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    if not multi_storage.has_constant(constant_id):
        raise HTTPException(status_code=404, detail=f"Mathematical constant '{constant_id}' not available")
    
    def build_task():
        try:
            print(f"🏗️  Starting cache build task for {constant_id}...")
            result = multi_storage.build_cache(constant_id, force_rebuild=force_rebuild)
            print(f"✅ Cache building completed: {result['status']}")
        except Exception as e:
            print(f"❌ Cache building failed for {constant_id}: {e}")
    
    background_tasks.add_task(build_task)
    
    constant_info = MATH_CONSTANTS[constant_id]
    return CacheBuildResponse(
        message=f"Cache building started for {constant_info.name} ({constant_info.symbol})",
        status="started",
        estimated_time_minutes=5
    )


@app.post("/admin/build-all-caches", response_model=BulkCacheBuildResponse)
async def build_all_caches(
    background_tasks: BackgroundTasks,
    force_rebuild: bool = Query(False, description="Force rebuild even if caches exist")
):
    """Build caches for ALL available mathematical constants (runs in background)"""
    if not multi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    available = multi_storage.get_available_constants()
    
    if not available:
        raise HTTPException(status_code=404, detail="No mathematical constants available")
    
    def build_all_task():
        try:
            print(f"🏗️  Starting bulk cache build for {len(available)} constant(s)...")
            results = multi_storage.build_all_caches(force_rebuild=force_rebuild)
            
            # Summary
            success = sum(1 for r in results if r["status"] == "success")
            skipped = sum(1 for r in results if r["status"] == "skipped")
            failed = sum(1 for r in results if r["status"] == "failed")
            
            print(f"✅ Bulk cache build complete: {success} success, {skipped} skipped, {failed} failed")
            
        except Exception as e:
            print(f"❌ Bulk cache building failed: {e}")
    
    background_tasks.add_task(build_all_task)
    
    return BulkCacheBuildResponse(
        message=f"Cache building started for {len(available)} mathematical constant(s)",
        status="started",
        total_constants=len(available),
        constants=available,
        force_rebuild=force_rebuild,
        estimated_time_minutes=len(available) * 5
    )


@app.post("/admin/verify/{constant_id}", response_model=VerificationResponse)
async def verify_integrity(
    constant_id: str = Path(..., description="Mathematical constant ID"),
    start: int = Query(0, ge=0, description="Start position for verification"),
    length: int = Query(10000, ge=100, le=100000, description="Length of segment"),
    sample_count: int = Query(10, ge=1, le=100, description="Number of random samples")
):
    """Verify data integrity for a specific constant across all storage sources"""
    if not multi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    if not multi_storage.has_constant(constant_id):
        raise HTTPException(status_code=404, detail=f"Mathematical constant '{constant_id}' not available")
    
    import random
    
    verification_results = []
    failed_verifications = []
    
    try:
        manager = multi_storage.get_manager(constant_id)
        
        for i in range(sample_count):
            pos = random.randint(start, start + length - 100)
            try:
                result = manager.get_digits(pos, 100, force_verify=True)
                verification_results.append({
                    "position": pos,
                    "verified": True,
                    "length": len(result)
                })
            except CorruptionError as e:
                failed_verifications.append({
                    "position": pos,
                    "error": str(e)
                })
        
        all_passed = len(failed_verifications) == 0
        
        from app.api.models.responses import VerificationResult, VerificationFailure
        
        return VerificationResponse(
            status="success" if all_passed else "partial_failure",
            verifications_completed=len(verification_results),
            all_passed=all_passed,
            failed_count=len(failed_verifications),
            results=[VerificationResult(**r) for r in verification_results],
            failures=[VerificationFailure(**f) for f in failed_verifications]
        )
        
    except CorruptionError as e:
        raise HTTPException(status_code=500, detail=f"Corruption detected: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint with basic information"""
    if not multi_storage:
        available_count = 0
        cached_count = 0
    else:
        available = multi_storage.get_available_constants()
        available_count = len(available)
        cached_count = sum(1 for cid in available if multi_storage.get_manager(cid).has_sqlite_cache())
    
    return {
        "message": "Math Constants Storage API - Multi-Constant Support",
        "version": settings.api_version,
        "status": "operational",
        "available_constants": available_count,
        "cached_constants": cached_count,
        "documentation": "/docs",
        "health_check": "/health",
        "list_constants": "/constants"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.api_host, 
        port=settings.api_port,
        reload=settings.hot_reload
    )