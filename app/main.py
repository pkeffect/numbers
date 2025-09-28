# app/main.py
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import asyncio
import time
from contextlib import asynccontextmanager

# Import our storage system
from app.storage.base_storage import MathConstantStorage, StorageConfig, CorruptionError

# Global storage instance
math_storage: Optional[MathConstantStorage] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize storage on startup"""
    global math_storage
    
    try:
        print("🔧 Initializing Math Constants Storage System...")
        config = StorageConfig()
        print(f"📁 Looking for pi file at: {config.original_file}")
        
        math_storage = MathConstantStorage(config)
        print("✅ Math constant storage system initialized successfully")
        yield
    except Exception as e:
        print(f"❌ Failed to initialize math storage: {e}")
        print("⚠️  System will start but endpoints will return 503 errors")
        print("💡 Make sure your pi_digits.txt file is in the data/ directory")
        yield
    finally:
        print("🛑 Shutting down math storage system")

app = FastAPI(
    title="Math Constants API - Triple Redundancy Storage",
    description="High-accuracy API for accessing billions of digits of mathematical constants",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class DigitsResponse(BaseModel):
    digits: str
    start_position: int
    length: int
    verified: bool
    retrieval_time_ms: float

class SearchResult(BaseModel):
    sequence: str
    positions: List[int]
    total_found: int
    search_time_ms: float

class StatsResponse(BaseModel):
    digit_frequencies: dict
    most_common: str
    least_common: str
    total_digits_analyzed: int
    analysis_time_ms: float

class HealthResponse(BaseModel):
    status: str
    sources_available: dict
    last_verification: str

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health and storage integrity"""
    print("❤️  Health check requested")
    
    if not math_storage:
        print("❌ Storage system not available")
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    try:
        print("🔍 Testing basic functionality...")
        # Test basic functionality
        test_digits = math_storage.get_digits(0, 10, force_verify=True)
        expected = "3141592653"
        
        sources_status = {
            "original_file": True,
            "sqlite_cache": True,
            "binary_cache": True
        }
        
        if test_digits == expected:
            print(f"✅ Health check passed - got {test_digits}")
            status = "healthy"
        else:
            print(f"⚠️  Health check degraded - got {test_digits}, expected {expected}")
            status = "degraded"
        
        return HealthResponse(
            status=status,
            sources_available=sources_status,
            last_verification=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        print(f"💥 Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

# Get digits endpoint
@app.get("/digits", response_model=DigitsResponse)
async def get_digits(
    start: int = Query(..., ge=0, description="Starting position (0-based)"),
    length: int = Query(..., ge=1, le=100000, description="Number of digits to retrieve"),
    verify: bool = Query(False, description="Force verification against original file")
):
    """Retrieve pi digits from specified position with optional verification"""
    if not pi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    start_time = time.time()
    
    try:
        digits = pi_storage.get_digits(start, length, force_verify=verify)
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
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Search for sequence
@app.get("/search", response_model=SearchResult)
async def search_sequence(
    sequence: str = Query(..., min_length=1, max_length=20, description="Digit sequence to search for"),
    max_results: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    start_from: int = Query(0, ge=0, description="Start search from position")
):
    """Search for a specific digit sequence in pi"""
    if not pi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    # Validate sequence contains only digits
    if not sequence.isdigit():
        raise HTTPException(status_code=400, detail="Sequence must contain only digits")
    
    start_time = time.time()
    positions = []
    
    try:
        # Simple search implementation (can be optimized with indexing)
        search_chunk_size = 100000
        current_pos = start_from
        
        while len(positions) < max_results and current_pos < pi_storage.file_source.get_file_size():
            chunk = pi_storage.get_digits(current_pos, search_chunk_size)
            
            # Find all occurrences in this chunk
            pos = 0
            while pos < len(chunk) - len(sequence) + 1:
                if chunk[pos:pos + len(sequence)] == sequence:
                    positions.append(current_pos + pos)
                    if len(positions) >= max_results:
                        break
                pos += 1
            
            current_pos += search_chunk_size - len(sequence) + 1
        
        search_time = (time.time() - start_time) * 1000
        
        return SearchResult(
            sequence=sequence,
            positions=positions,
            total_found=len(positions),
            search_time_ms=round(search_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Statistical analysis
@app.get("/stats", response_model=StatsResponse)
async def get_statistics(
    start: int = Query(0, ge=0, description="Start position for analysis"),
    sample_size: int = Query(100000, ge=1000, le=1000000, description="Number of digits to analyze")
):
    """Get statistical analysis of pi digits"""
    if not pi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    start_time = time.time()
    
    try:
        digits = pi_storage.get_digits(start, sample_size)
        
        # Count digit frequencies
        frequencies = {str(i): 0 for i in range(10)}
        for digit in digits:
            frequencies[digit] += 1
        
        # Convert to percentages
        percentages = {digit: (count / sample_size) * 100 
                      for digit, count in frequencies.items()}
        
        # Find most and least common
        most_common = max(percentages, key=percentages.get)
        least_common = min(percentages, key=percentages.get)
        
        analysis_time = (time.time() - start_time) * 1000
        
        return StatsResponse(
            digit_frequencies=percentages,
            most_common=most_common,
            least_common=least_common,
            total_digits_analyzed=sample_size,
            analysis_time_ms=round(analysis_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistical analysis failed: {str(e)}")

# Build caches endpoint
@app.post("/admin/build-caches")
async def build_caches(background_tasks: BackgroundTasks):
    """Build SQLite and binary caches (admin only)"""
    if not pi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    def build_task():
        try:
            pi_storage.build_caches()
        except Exception as e:
            print(f"Cache building failed: {e}")
    
    background_tasks.add_task(build_task)
    return {"message": "Cache building started in background"}

# Verify data integrity
@app.post("/admin/verify")
async def verify_integrity(
    start: int = Query(0, ge=0),
    length: int = Query(10000, ge=100, le=100000),
    sample_count: int = Query(10, ge=1, le=100)
):
    """Verify data integrity across all storage sources"""
    if not pi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    import random
    
    verification_results = []
    
    try:
        for _ in range(sample_count):
            pos = random.randint(start, start + length - 100)
            result = pi_storage.get_digits(pos, 100, force_verify=True)
            verification_results.append({
                "position": pos,
                "verified": True,
                "length": len(result)
            })
        
        return {
            "status": "success",
            "verifications_completed": len(verification_results),
            "all_passed": True,
            "results": verification_results
        }
    
    except CorruptionError as e:
        raise HTTPException(status_code=500, detail=f"Corruption detected: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")

# Random digits endpoint (for creative applications)
@app.get("/random")
async def get_random_digits(
    length: int = Query(10, ge=1, le=1000, description="Number of random digits"),
    seed: Optional[int] = Query(None, description="Seed for reproducible randomness")
):
    """Get 'random' digits from a random position in pi"""
    if not pi_storage:
        raise HTTPException(status_code=503, detail="Storage system not initialized")
    
    import random
    
    if seed is not None:
        random.seed(seed)
    
    max_start = pi_storage.file_source.get_file_size() - length
    random_start = random.randint(0, max_start)
    
    try:
        digits = pi_storage.get_digits(random_start, length)
        return {
            "digits": digits,
            "position": random_start,
            "length": length,
            "seed_used": seed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)