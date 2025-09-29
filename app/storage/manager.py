# app/storage/manager.py
import os
import random
import time
from typing import Optional, List
from dataclasses import dataclass

from app.storage.file_source import FileSource
from app.storage.sqlite_source import SQLiteSource
from app.storage.binary_source import BinarySource
from app.core.exceptions import CorruptionError, StorageError
from app.core.constants import KNOWN_PREFIXES

@dataclass
class StorageConfig:
    """Configuration for storage system"""
    original_file: str = "/app/data/pi_digits.txt"
    sqlite_db: str = "/app/data/pi_chunks.db"
    binary_file: str = "/app/data/pi_binary.dat"
    chunk_size: int = 10000  # digits per chunk
    verify_every: int = 100  # verify every N requests

class MathConstantManager:
    """Main manager for mathematical constant storage with triple redundancy"""
    
    def __init__(self, config: StorageConfig):
        self.config = config
        self.request_count = 0
        
        print(f"🔧 Initializing storage with config:")
        print(f"   📁 Original file: {config.original_file}")
        print(f"   🗄️  SQLite DB: {config.sqlite_db}")
        print(f"   💾 Binary file: {config.binary_file}")
        
        # Check if original file exists
        if not os.path.exists(config.original_file):
            print(f"❌ Original file not found: {config.original_file}")
            print(f"💡 Available files in data directory:")
            data_dir = os.path.dirname(config.original_file)
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if file.endswith('.txt'):
                        print(f"   📄 {file}")
            raise FileNotFoundError(f"Math constant file not found: {config.original_file}")
        
        # Initialize all storage sources
        print("🔧 Initializing file source...")
        self.file_source = FileSource(config.original_file)
        
        print("🔧 Initializing SQLite source...")
        self.sqlite_source = SQLiteSource(config.sqlite_db)
        
        print("🔧 Initializing binary source...")
        self.binary_source = BinarySource(config.binary_file)
        
        # Verify file integrity on startup
        print("🔍 Verifying file integrity...")
        self._verify_integrity()
        print("✅ Storage initialization complete!")
    
    def get_digits(self, start: int, length: int, force_verify: bool = False) -> str:
        """Get digits with triple redundancy and verification"""
        self.request_count += 1
        
        # Determine if we should verify this request
        should_verify = (force_verify or 
                        self.request_count % self.config.verify_every == 0)
        
        try:
            # Try SQLite first (fastest for random access)
            if self.has_sqlite_cache():
                try:
                    result = self.sqlite_source.get(start, length)
                    
                    if should_verify:
                        # Verify against original file
                        file_result = self._get_cleaned_digits_from_file(start, length)
                        
                        if result != file_result:
                            raise CorruptionError(f"SQLite corruption at position {start}")
                        
                        # Also verify binary if available
                        if self.has_binary_cache():
                            try:
                                binary_result = self.binary_source.get(start, length)
                                if result != binary_result:
                                    raise CorruptionError(f"Binary corruption at position {start}")
                            except FileNotFoundError:
                                pass  # Binary might not be fully built yet
                    
                    return result
                except (ValueError, CorruptionError):
                    print(f"SQLite cache failed for position {start}, falling back to file")
                    pass
            
            # Fallback to original file (most reliable)
            return self._get_cleaned_digits_from_file(start, length)
            
        except Exception as e:
            print(f"All sources failed: {e}, attempting file fallback")
            # Last resort fallback to original file
            return self._get_cleaned_digits_from_file(start, length)
    
    def search_sequence(self, sequence: str, max_results: int = 100, start_from: int = 0) -> List[int]:
        """Search for a specific digit sequence"""
        positions = []
        search_chunk_size = 100000
        current_pos = start_from
        
        try:
            file_size = self.get_file_size()
            
            while len(positions) < max_results and current_pos < file_size:
                # Ensure we don't read past the end
                remaining = file_size - current_pos
                chunk_size = min(search_chunk_size, remaining)
                
                if chunk_size < len(sequence):
                    break
                
                chunk = self.get_digits(current_pos, chunk_size)
                
                # Find all occurrences in this chunk
                pos = 0
                while pos < len(chunk) - len(sequence) + 1:
                    if chunk[pos:pos + len(sequence)] == sequence:
                        positions.append(current_pos + pos)
                        if len(positions) >= max_results:
                            break
                    pos += 1
                
                # Move to next chunk with overlap to catch sequences spanning chunks
                current_pos += search_chunk_size - len(sequence) + 1
            
            return positions
            
        except Exception as e:
            raise StorageError(f"Search failed: {e}")
    
    def _get_cleaned_digits_from_file(self, start: int, length: int) -> str:
        """Get digits from file, handling decimal points and formatting"""
        # Read a bit more to account for potential decimal points
        buffer_size = length + 10  # Extra buffer for decimal points
        raw_content = self.file_source.get(start, buffer_size)
        
        # Clean the content
        cleaned_content = raw_content.replace('.', '').replace(' ', '').replace('\n', '').replace('\r', '')
        
        # Return exactly the requested length
        return cleaned_content[:length]
    
    def build_caches(self, progress_callback=None):
        """Build SQLite and binary caches from original file"""
        print("🏗️  Building caches from original file...")
        
        try:
            file_size = self.get_file_size()
            chunks_total = (file_size + self.config.chunk_size - 1) // self.config.chunk_size
            
            print(f"📊 File size: {file_size:,} characters")
            print(f"📦 Will create {chunks_total:,} chunks of {self.config.chunk_size:,} digits each")
            
            for chunk_id in range(chunks_total):
                start_pos = chunk_id * self.config.chunk_size
                chunk_length = min(self.config.chunk_size, file_size - start_pos)
                
                # Read from original file
                chunk_data = self._get_cleaned_digits_from_file(start_pos, chunk_length)
                
                # Store in both caches
                print(f"💾 Storing chunk {chunk_id + 1}/{chunks_total} (position {start_pos:,})")
                self.sqlite_source.store_chunk(chunk_id, start_pos, chunk_data)
                self.binary_source.store_chunk(start_pos, chunk_data)
                
                if progress_callback:
                    progress_callback(chunk_id + 1, chunks_total)
            
            print("✅ Cache building complete!")
            print(f"📁 Cache files created:")
            print(f"   🗄️  SQLite: {self.config.sqlite_db}")
            print(f"   💾 Binary: {self.config.binary_file}")
            
        except Exception as e:
            print(f"❌ Cache building failed: {e}")
            raise StorageError(f"Cache building failed: {e}")
    
    def _verify_integrity(self):
        """Verify known mathematical constants with flexible format handling"""
        print(f"🔍 Verifying file format and content...")
        
        try:
            # Read first 60 characters to handle potential decimal points
            raw_content = self.file_source.get(0, 60)
            print(f"📖 Raw content from file: {raw_content}")
            
            # Clean the content - remove decimal points and any whitespace
            cleaned_content = raw_content.replace('.', '').replace(' ', '').replace('\n', '').replace('\r', '')
            print(f"🧹 Cleaned content: {cleaned_content}")
            
            # Get first 50 digits for verification
            actual_digits = cleaned_content[:50]
            print(f"🔢 First 50 digits: {actual_digits}")
            
            # Try to identify the mathematical constant
            constant_found = None
            for constant_name, known_prefix in KNOWN_PREFIXES.items():
                if actual_digits == known_prefix:
                    constant_found = constant_name
                    break
            
            if constant_found:
                from app.core.constants import MATH_CONSTANTS
                constant_info = MATH_CONSTANTS[constant_found]
                print(f"✅ Successfully identified: {constant_info.name} ({constant_info.symbol})")
            else:
                print("❓ Could not identify this mathematical constant from known values")
                print("📄 Proceeding anyway - assuming this is a valid mathematical constant")
            
            # Verify digits are all numeric
            if not actual_digits.isdigit():
                raise CorruptionError(f"File contains non-digit characters: {actual_digits}")
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            raise CorruptionError(f"Cannot read from file: {e}")
            
        print("✅ File integrity check complete!")
    
    def has_sqlite_cache(self) -> bool:
        """Check if SQLite cache exists and has data"""
        try:
            return self.sqlite_source.has_data()
        except:
            return False
    
    def has_binary_cache(self) -> bool:
        """Check if binary cache exists"""
        return os.path.exists(self.config.binary_file) and os.path.getsize(self.config.binary_file) > 0
    
    def get_file_size(self) -> int:
        """Get total file size in characters"""
        return self.file_source.get_file_size()
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'file_source'):
                self.file_source.close()
            if hasattr(self, 'sqlite_source'):
                self.sqlite_source.close()
            if hasattr(self, 'binary_source'):
                self.binary_source.close()
        except Exception as e:
            print(f"Warning: Error during cleanup: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup()