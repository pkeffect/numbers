# app/api/routers/admin.py
"""Admin endpoints for bulk operations and system maintenance"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional

from app.storage.multi_manager import MultiConstantManager
from app.api.models.responses import BulkCacheBuildResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

_storage: Optional[MultiConstantManager] = None

def set_storage(storage: MultiConstantManager):
    global _storage
    _storage = storage

def get_storage():
    if not _storage:
        raise HTTPException(503, "Storage not initialized")
    return _storage

@router.post("/build-all-caches", response_model=BulkCacheBuildResponse)
async def build_all_caches(
    background_tasks: BackgroundTasks,
    force_rebuild: bool = Query(False, description="Force rebuild existing caches")
):
    """
    Build caches for ALL available mathematical constants.
    
    This endpoint initiates cache building for all constants that have data files.
    The operation runs in the background to avoid blocking the API.
    
    Args:
        force_rebuild: If False (default), skips constants that already have complete caches.
                      If True, rebuilds all caches regardless of existing cache status.
    
    Returns:
        - message: Status message
        - status: Operation status ('started')
        - total_constants: Number of constants to process
        - constants: List of constant IDs being processed
        - force_rebuild: Whether forcing rebuild
        - estimated_time_minutes: Estimated total time
    
    Example:
        # Build only missing caches (smart, recommended)
        POST /admin/build-all-caches
        
        # Force rebuild all caches (slower, use for verification)
        POST /admin/build-all-caches?force_rebuild=true
    
    Notes:
        - Process runs in background, API remains responsive
        - Check individual constant status endpoints to monitor progress
        - Logs show detailed progress during cache building
        - Each constant takes ~5 minutes per GB of data
    """
    storage = get_storage()
    available = storage.get_available_constants()
    
    if not available:
        raise HTTPException(404, "No mathematical constants available")
    
    def build_task():
        """Background task for building all caches"""
        try:
            print(f"🏗️  Starting bulk cache build for {len(available)} constant(s)...")
            print(f"   Force rebuild: {force_rebuild}")
            
            results = storage.build_all_caches(force_rebuild=force_rebuild)
            
            # Summary statistics
            success = sum(1 for r in results if r.get("status") == "success")
            skipped = sum(1 for r in results if r.get("status") == "skipped")
            failed = sum(1 for r in results if r.get("status") == "failed")
            
            print(f"\n{'='*60}")
            print(f"✅ Bulk cache build complete!")
            print(f"   Success: {success}")
            print(f"   Skipped: {skipped}")
            print(f"   Failed: {failed}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Bulk cache build failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Start the background task
    background_tasks.add_task(build_task)
    
    return BulkCacheBuildResponse(
        message=f"Cache building started for {len(available)} mathematical constant(s)",
        status="started",
        total_constants=len(available),
        constants=available,
        force_rebuild=force_rebuild,
        estimated_time_minutes=len(available) * 5
    )

@router.get("/status")
async def admin_status():
    """
    Get administrative status and system information.
    
    Returns:
        - System statistics
        - Cache status summary
        - Available operations
    """
    storage = get_storage()
    available = storage.get_available_constants()
    
    # Gather statistics
    total_constants = len(available)
    cached_constants = sum(1 for cid in available if storage.get_manager(cid).has_sqlite_cache())
    
    # Get detailed status for each constant
    constant_details = {}
    for constant_id in available:
        try:
            status = storage.get_constant_status(constant_id)
            constant_details[constant_id] = {
                "name": status.name,
                "symbol": status.symbol,
                "file_exists": status.file_exists,
                "file_size_mb": round(status.file_size / (1024 * 1024), 2),
                "cache_exists": status.cache_exists,
                "cache_complete": status.cache_complete,
                "cached_digits": status.cached_digits
            }
        except Exception as e:
            constant_details[constant_id] = {"error": str(e)}
    
    return {
        "system": {
            "total_constants": total_constants,
            "cached_constants": cached_constants,
            "cache_percentage": round((cached_constants / total_constants * 100) if total_constants > 0 else 0, 2)
        },
        "constants": constant_details,
        "operations": {
            "build_all_caches": "/admin/build-all-caches",
            "build_single_cache": "/{constant}/build-cache",
            "verify_constant": "/{constant}/verify"
        }
    }