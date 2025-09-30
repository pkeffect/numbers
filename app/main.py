# app/main.py
"""
Math Constants Storage System - Main Application
Refactored with dedicated routers for each constant.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional

from app.storage.multi_manager import MultiConstantManager
from app.core.config import settings

# Import all routers
from app.api.routers import (
    pi, e, phi, sqrt2, sqrt3,
    catalan, eulers, lemniscate,
    log2, log3, log10, zeta3,
    general, admin, legacy
)

multi_storage: Optional[MultiConstantManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize storage on startup and cleanup on shutdown"""
    global multi_storage
    
    try:
        print("🔧 Initializing Math Constants Multi-Storage System...")
        multi_storage = MultiConstantManager()
        
        available = multi_storage.get_available_constants()
        print(f"✅ Initialized successfully with {len(available)} constant(s)")
        
        cached_count = sum(1 for cid in available if multi_storage.get_manager(cid).has_sqlite_cache())
        print(f"💾 Cached constants: {cached_count}/{len(available)}")
        
        # Inject storage into all routers
        for router_module in [pi, e, phi, sqrt2, sqrt3, catalan, eulers, 
                               lemniscate, log2, log3, log10, zeta3, general, admin, legacy]:
            router_module.set_storage(multi_storage)
        
        yield
        
    except Exception as ex:
        print(f"❌ Failed to initialize: {ex}")
        yield
        
    finally:
        print("🛑 Shutting down")
        if multi_storage:
            multi_storage.cleanup()

app = FastAPI(
    title=settings.api_title + " - Dedicated Endpoints",
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Include all routers
app.include_router(general.router)
app.include_router(admin.router)
app.include_router(legacy.router)  # Legacy parameterized endpoints
app.include_router(pi.router)
app.include_router(e.router)
app.include_router(phi.router)
app.include_router(sqrt2.router)
app.include_router(sqrt3.router)
app.include_router(catalan.router)
app.include_router(eulers.router)
app.include_router(lemniscate.router)
app.include_router(log2.router)
app.include_router(log3.router)
app.include_router(log10.router)
app.include_router(zeta3.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port, reload=settings.hot_reload)