# app/api/routers/general.py
"""General endpoints (root, health, list constants)"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import time

from app.storage.multi_manager import MultiConstantManager
from app.core.constants import MATH_CONSTANTS
from app.api.models.responses import (
    MultiConstantHealthResponse,
    ConstantsListResponse,
    ConstantInfo
)

router = APIRouter(tags=["General"])

_storage: Optional[MultiConstantManager] = None

def set_storage(storage: MultiConstantManager):
    global _storage
    _storage = storage

def get_storage():
    if not _storage:
        raise HTTPException(503, "Storage not initialized")
    return _storage

@router.get("/")
async def root():
    """API root endpoint"""
    storage = get_storage()
    available = storage.get_available_constants()
    cached_count = sum(1 for cid in available if storage.get_manager(cid).has_sqlite_cache())
    
    return {
        "message": "Math Constants API - Dedicated Endpoints",
        "version": "2.0.0",
        "available_constants": len(available),
        "cached_constants": cached_count,
        "documentation": "/docs",
        "health": "/health",
        "constants": "/constants"
    }

@router.get("/health", response_model=MultiConstantHealthResponse)
async def health_check():
    """System health check across all constants"""
    storage = get_storage()
    available = storage.get_available_constants()
    
    if not available:
        raise HTTPException(503, "No constants available")
    
    # Test basic functionality
    test_constant = available[0]
    test_passed = len(storage.get_manager(test_constant).get_digits(0, 10, force_verify=True)) == 10
    
    # Build cache status
    constants_status = {cid: storage.get_manager(cid).has_sqlite_cache() for cid in available}
    cached_count = sum(constants_status.values())
    
    # Determine overall status
    if test_passed and cached_count == len(available):
        status = "healthy"
    elif test_passed and cached_count > 0:
        status = "degraded"
    else:
        status = "unhealthy"
    
    return MultiConstantHealthResponse(
        status=status,
        total_constants=len(available),
        cached_constants=cached_count,
        constants_status=constants_status,
        available_constants=available,
        last_verification=time.strftime("%Y-%m-%d %H:%M:%S"),
        test_passed=test_passed
    )

@router.get("/constants", response_model=ConstantsListResponse)
async def list_constants():
    """List all mathematical constants with status"""
    storage = get_storage()
    statuses = storage.get_all_statuses()
    available_ids = storage.get_available_constants()
    
    constants_info = []
    available_count = 0
    cached_count = 0
    
    for constant_id, status in statuses.items():
        is_available = constant_id in available_ids
        is_cached = False
        
        if is_available:
            available_count += 1
            is_cached = storage.get_manager(constant_id).has_sqlite_cache()
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