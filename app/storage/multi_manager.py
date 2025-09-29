# app/storage/multi_manager.py
"""
Multi-Constant Manager

Manages multiple mathematical constants simultaneously with smart cache detection.
"""

import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from app.storage.manager import MathConstantManager, StorageConfig
from app.core.constants import MATH_CONSTANTS, CONSTANT_FILES
from app.core.exceptions import StorageError
from app.core.config import settings


@dataclass
class ConstantStatus:
    """Status information for a mathematical constant"""
    name: str
    symbol: str
    file_exists: bool
    file_path: str
    cache_exists: bool
    cache_complete: bool
    file_size: int
    cached_digits: int
    

class MultiConstantManager:
    """Manager for multiple mathematical constants"""
    
    def __init__(self):
        self.managers: Dict[str, MathConstantManager] = {}
        self.available_constants: List[str] = []
        
        print("🔧 Initializing Multi-Constant Manager...")
        self._discover_and_initialize_constants()
        print(f"✅ Initialized {len(self.managers)} mathematical constant(s)")
    
    def _discover_and_initialize_constants(self):
        """Discover and initialize all available mathematical constants"""
        
        for constant_id, constant_info in MATH_CONSTANTS.items():
            try:
                # Get file path from settings
                file_path = self._get_file_path(constant_id)
                
                if not os.path.exists(file_path):
                    print(f"⏭️  Skipping {constant_info.name} - file not found: {file_path}")
                    continue
                
                # Check file size to ensure it's not empty
                file_size = os.path.getsize(file_path)
                if file_size < 100:
                    print(f"⏭️  Skipping {constant_info.name} - file too small: {file_size} bytes")
                    continue
                
                # Create storage config for this constant
                config = StorageConfig(
                    original_file=file_path,
                    sqlite_db=self._get_sqlite_path(constant_id),
                    binary_file=self._get_binary_path(constant_id),
                    chunk_size=settings.chunk_size,
                    verify_every=settings.verify_every
                )
                
                # Initialize manager for this constant
                print(f"📊 Initializing {constant_info.name} ({constant_info.symbol})...")
                manager = MathConstantManager(config)
                
                self.managers[constant_id] = manager
                self.available_constants.append(constant_id)
                
                # Check cache status
                cache_status = "✅ cached" if manager.has_sqlite_cache() else "❌ not cached"
                print(f"   Status: {cache_status}")
                
            except Exception as e:
                print(f"❌ Failed to initialize {constant_info.name}: {e}")
                continue
    
    def _get_file_path(self, constant_id: str) -> str:
        """Get file path for a constant from settings"""
        path_mapping = {
            "catalan": settings.catalan_file_path,
            "e": settings.e_file_path,
            "eulers": settings.eulers_file_path,
            "lemniscate": settings.lemniscate_file_path,
            "log10": settings.log10_file_path,
            "log2": settings.log2_file_path,
            "log3": settings.log3_file_path,
            "phi": settings.phi_file_path,
            "pi": settings.pi_file_path,
            "sqrt2": settings.sqrt2_file_path,
            "sqrt3": settings.sqrt3_file_path,
            "zeta3": settings.zeta3_file_path,
        }
        return path_mapping.get(constant_id, f"/app/data/{constant_id}_digits.txt")
    
    def _get_sqlite_path(self, constant_id: str) -> str:
        """Get SQLite database path for a constant"""
        path_mapping = {
            "catalan": settings.catalan_sqlite_db,
            "e": settings.e_sqlite_db,
            "eulers": settings.eulers_sqlite_db,
            "lemniscate": settings.lemniscate_sqlite_db,
            "log10": settings.log10_sqlite_db,
            "log2": settings.log2_sqlite_db,
            "log3": settings.log3_sqlite_db,
            "phi": settings.phi_sqlite_db,
            "pi": settings.pi_sqlite_db,
            "sqrt2": settings.sqrt2_sqlite_db,
            "sqrt3": settings.sqrt3_sqlite_db,
            "zeta3": settings.zeta3_sqlite_db,
        }
        return path_mapping.get(constant_id, f"/app/data/{constant_id}_chunks.db")
    
    def _get_binary_path(self, constant_id: str) -> str:
        """Get binary file path for a constant"""
        path_mapping = {
            "catalan": settings.catalan_binary_file,
            "e": settings.e_binary_file,
            "eulers": settings.eulers_binary_file,
            "lemniscate": settings.lemniscate_binary_file,
            "log10": settings.log10_binary_file,
            "log2": settings.log2_binary_file,
            "log3": settings.log3_binary_file,
            "phi": settings.phi_binary_file,
            "pi": settings.pi_binary_file,
            "sqrt2": settings.sqrt2_binary_file,
            "sqrt3": settings.sqrt3_binary_file,
            "zeta3": settings.zeta3_binary_file,
        }
        return path_mapping.get(constant_id, f"/app/data/{constant_id}_binary.dat")
    
    def get_manager(self, constant_id: str) -> MathConstantManager:
        """Get manager for a specific constant"""
        if constant_id not in self.managers:
            raise StorageError(f"Mathematical constant '{constant_id}' not available")
        return self.managers[constant_id]
    
    def has_constant(self, constant_id: str) -> bool:
        """Check if a constant is available"""
        return constant_id in self.managers
    
    def get_available_constants(self) -> List[str]:
        """Get list of available constant IDs"""
        return self.available_constants.copy()
    
    def get_constant_status(self, constant_id: str) -> ConstantStatus:
        """Get detailed status for a constant"""
        if constant_id not in MATH_CONSTANTS:
            raise ValueError(f"Unknown constant: {constant_id}")
        
        constant_info = MATH_CONSTANTS[constant_id]
        file_path = self._get_file_path(constant_id)
        
        # Check file existence
        file_exists = os.path.exists(file_path)
        file_size = os.path.getsize(file_path) if file_exists else 0
        
        # Check cache status
        cache_exists = False
        cache_complete = False
        cached_digits = 0
        
        if constant_id in self.managers:
            manager = self.managers[constant_id]
            cache_exists = manager.has_sqlite_cache()
            
            if cache_exists:
                # Check if cache covers the full file
                sqlite_source = manager.sqlite_source
                coverage_start, coverage_end = sqlite_source.get_coverage_range()
                cached_digits = coverage_end - coverage_start
                cache_complete = cached_digits >= file_size - 10  # Allow small margin
        
        return ConstantStatus(
            name=constant_info.name,
            symbol=constant_info.symbol,
            file_exists=file_exists,
            file_path=file_path,
            cache_exists=cache_exists,
            cache_complete=cache_complete,
            file_size=file_size,
            cached_digits=cached_digits
        )
    
    def get_all_statuses(self) -> Dict[str, ConstantStatus]:
        """Get status for all constants"""
        statuses = {}
        for constant_id in MATH_CONSTANTS.keys():
            try:
                statuses[constant_id] = self.get_constant_status(constant_id)
            except Exception as e:
                print(f"Warning: Could not get status for {constant_id}: {e}")
        return statuses
    
    def build_cache(self, constant_id: str, force_rebuild: bool = False, progress_callback=None) -> dict:
        """Build cache for a specific constant"""
        if constant_id not in self.managers:
            raise StorageError(f"Cannot build cache - constant '{constant_id}' not initialized")
        
        manager = self.managers[constant_id]
        constant_info = MATH_CONSTANTS[constant_id]
        
        # Check if cache already exists and is complete
        if not force_rebuild:
            status = self.get_constant_status(constant_id)
            if status.cache_exists and status.cache_complete:
                print(f"✅ Cache for {constant_info.name} already exists and is complete - skipping")
                return {
                    "constant": constant_id,
                    "name": constant_info.name,
                    "status": "skipped",
                    "reason": "Cache already complete",
                    "cached_digits": status.cached_digits
                }
        
        # Build the cache
        print(f"🏗️  Building cache for {constant_info.name} ({constant_info.symbol})...")
        try:
            manager.build_caches(progress_callback=progress_callback)
            
            # Verify the build
            status = self.get_constant_status(constant_id)
            
            return {
                "constant": constant_id,
                "name": constant_info.name,
                "status": "success",
                "cached_digits": status.cached_digits,
                "cache_complete": status.cache_complete
            }
        except Exception as e:
            print(f"❌ Failed to build cache for {constant_info.name}: {e}")
            return {
                "constant": constant_id,
                "name": constant_info.name,
                "status": "failed",
                "error": str(e)
            }
    
    def build_all_caches(self, force_rebuild: bool = False, progress_callback=None) -> List[dict]:
        """Build caches for all available constants"""
        results = []
        
        print(f"🏗️  Building caches for {len(self.available_constants)} constant(s)...")
        print(f"   Force rebuild: {force_rebuild}")
        
        for i, constant_id in enumerate(self.available_constants, 1):
            constant_info = MATH_CONSTANTS[constant_id]
            print(f"\n[{i}/{len(self.available_constants)}] Processing {constant_info.name}...")
            
            result = self.build_cache(constant_id, force_rebuild=force_rebuild, progress_callback=progress_callback)
            results.append(result)
        
        # Summary
        print("\n" + "="*60)
        print("📊 Cache Building Summary:")
        print("="*60)
        
        success_count = sum(1 for r in results if r["status"] == "success")
        skipped_count = sum(1 for r in results if r["status"] == "skipped")
        failed_count = sum(1 for r in results if r["status"] == "failed")
        
        print(f"✅ Successfully built: {success_count}")
        print(f"⏭️  Skipped (already complete): {skipped_count}")
        print(f"❌ Failed: {failed_count}")
        print("="*60)
        
        return results
    
    def cleanup(self):
        """Cleanup all managers"""
        for manager in self.managers.values():
            try:
                manager.cleanup()
            except Exception as e:
                print(f"Warning: Error during cleanup: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup()