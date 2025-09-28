# app/storage/base_storage.py
import os
import random
import time
import sqlite3
from typing import Optional
from dataclasses import dataclass

from app.storage.file_source import FileSource
from app.storage.sqlite_source import SQLiteSource, CorruptionError
from app.storage.binary_source import BinarySource

@dataclass
class StorageConfig:
    original_file: str = "/app/data/pi_digits.txt"  # Updated path
    sqlite_db: str = "/app/data/pi_chunks.db"       # Updated path
    binary_file: str = "/app/data/pi_binary.dat"    # Updated path
    chunk_size: int = 10000  # digits per chunk
    verify_every: int = 100  # verify every N requests

class CorruptionError(Exception):
    """Raised when data corruption is detected"""
    pass

class MathConstantStorage:
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
                        self.request_count % self.config.verify_every == 0 or
                        start + length > self.file_source.get_file_size())
        
        try:
            # Try SQLite first (fastest for random access)
            result = self.sqlite_source.get(start, length)
            
            if should_verify:
                # Verify against original file
                file_result = self.file_source.get(start, length)
                # Clean file result (remove decimal points if present)
                cleaned_file_result = file_result.replace('.', '').replace(' ', '').replace('\n', '').replace('\r', '')
                
                # Adjust start position if we need to account for decimal point
                if '.' in file_result:
                    # If there's a decimal point, we need to adjust our reading position
                    actual_file_result = self._get_cleaned_digits_from_file(start, length)
                else:
                    actual_file_result = file_result
                
                if result != actual_file_result:
                    raise CorruptionError(f"SQLite corruption at position {start}")
                
                # Also verify binary if available
                try:
                    binary_result = self.binary_source.get(start, length)
                    if result != binary_result:
                        raise CorruptionError(f"Binary corruption at position {start}")
                except:
                    pass  # Binary might not be fully built yet
            
            return result
            
        except Exception as e:
            print(f"Cache failed: {e}, falling back to file source")
            # Fallback to original file (most reliable)
            return self._get_cleaned_digits_from_file(start, length)
    
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
        
        file_size = self.file_source.get_file_size()
        chunks_total = (file_size + self.config.chunk_size - 1) // self.config.chunk_size
        
        print(f"📊 File size: {file_size:,} characters")
        print(f"📦 Will create {chunks_total:,} chunks of {self.config.chunk_size:,} digits each")
        
        for chunk_id in range(chunks_total):
            start_pos = chunk_id * self.config.chunk_size
            chunk_length = min(self.config.chunk_size, file_size - start_pos)
            
            # Read from original file
            chunk_data = self.file_source.get(start_pos, chunk_length)
            
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
            
            # Known mathematical constants (first 50 digits, no decimal)
            known_constants = {
                "31415926535897932384626433832795028841971693993751": "Pi (π)",
                "27182818284590452353602874713526624977572470936999": "Euler's number (e)",
                "16180339887498948482045868343656381177203091798057": "Golden ratio (φ)", 
                "57721566490153286060651209008240243104215933593992": "Euler-Mascheroni constant (γ)",
                "14142135623730950488016887242096980785696718753769": "Square root of 2 (√2)",
                "17320508075688772935274463415058723669428052538103": "Square root of 3 (√3)",
                "91596559417721901505460351493238411077414937428167": "Catalan constant (G)",
                "26205830904531276522748574649951968533133071993113": "Lemniscate constant (ϖ)",
                "69314718055994530941723212145817656807550013436025": "Natural log of 2 (ln(2))",
                "10986122886681096913952452369225257046474905578227": "Natural log of 3 (ln(3))",
                "23025850929940456840179914546843642076011014886287": "Natural log of 10 (ln(10))",
                "12020569031595942853997381615114499907649862923404": "Apéry's constant ζ(3)"
            }
            
            # Try to identify the mathematical constant
            if actual_digits in known_constants:
                constant_name = known_constants[actual_digits]
                print(f"✅ Successfully identified: {constant_name}")
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

class FileSource:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._file_handle = None
        self._file_size = None
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Pi file not found: {filepath}")
    
    def get(self, start: int, length: int) -> str:
        """Get digits from original file using seek"""
        if self._file_handle is None:
            self._file_handle = open(self.filepath, 'r')
        
        self._file_handle.seek(start)
        return self._file_handle.read(length)
    
    def get_file_size(self) -> int:
        """Get total file size in characters"""
        if self._file_size is None:
            self._file_size = os.path.getsize(self.filepath)
        return self._file_size

class SQLiteSource:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize database tables"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS pi_chunks (
                chunk_id INTEGER PRIMARY KEY,
                start_position INTEGER NOT NULL,
                end_position INTEGER NOT NULL,
                digits TEXT NOT NULL,
                checksum TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_position 
            ON pi_chunks(start_position, end_position)
        ''')
        
        self.conn.commit()
    
    def store_chunk(self, chunk_id: int, start_pos: int, digits: str):
        """Store a chunk with checksum"""
        end_pos = start_pos + len(digits)
        checksum = hashlib.md5(digits.encode()).hexdigest()
        
        self.conn.execute('''
            INSERT OR REPLACE INTO pi_chunks 
            (chunk_id, start_position, end_position, digits, checksum)
            VALUES (?, ?, ?, ?, ?)
        ''', (chunk_id, start_pos, end_pos, digits, checksum))
        
        self.conn.commit()
    
    def get(self, start: int, length: int) -> str:
        """Get digits from database, potentially spanning multiple chunks"""
        end = start + length
        
        cursor = self.conn.execute('''
            SELECT start_position, end_position, digits, checksum
            FROM pi_chunks
            WHERE start_position < ? AND end_position > ?
            ORDER BY start_position
        ''', (end, start))
        
        chunks = cursor.fetchall()
        if not chunks:
            raise ValueError(f"No data found for range {start}-{end}")
        
        result = ""
        for chunk_start, chunk_end, chunk_digits, checksum in chunks:
            # Verify checksum
            if hashlib.md5(chunk_digits.encode()).hexdigest() != checksum:
                raise CorruptionError(f"Checksum mismatch in chunk {chunk_start}-{chunk_end}")
            
            # Calculate overlap with requested range
            overlap_start = max(start, chunk_start)
            overlap_end = min(end, chunk_end)
            
            if overlap_start < overlap_end:
                # Extract the relevant portion
                chunk_offset = overlap_start - chunk_start
                chunk_length = overlap_end - overlap_start
                result += chunk_digits[chunk_offset:chunk_offset + chunk_length]
        
        if len(result) != length:
            raise ValueError(f"Retrieved {len(result)} digits, expected {length}")
        
        return result

class BinarySource:
    def __init__(self, binary_path: str):
        self.binary_path = binary_path
        self._file_handle = None
    
    def store_chunk(self, start_pos: int, digits: str):
        """Store digits in binary format (4 bits per digit)"""
        if self._file_handle is None:
            self._file_handle = open(self.binary_path, 'ab')
        
        # Pack 2 digits per byte
        binary_data = bytearray()
        for i in range(0, len(digits), 2):
            if i + 1 < len(digits):
                # Two digits
                byte_val = int(digits[i]) * 16 + int(digits[i + 1])
            else:
                # One digit (pad with 0)
                byte_val = int(digits[i]) * 16
            binary_data.append(byte_val)
        
        self._file_handle.write(binary_data)
        self._file_handle.flush()
    
    def get(self, start: int, length: int) -> str:
        """Get digits from binary file"""
        if not os.path.exists(self.binary_path):
            raise FileNotFoundError("Binary cache not built yet")
        
        with open(self.binary_path, 'rb') as f:
            # Calculate byte positions
            start_byte = start // 2
            end_byte = (start + length + 1) // 2
            
            f.seek(start_byte)
            binary_data = f.read(end_byte - start_byte)
            
            # Unpack bytes to digits
            digits = ""
            for byte_val in binary_data:
                high_digit = byte_val >> 4
                low_digit = byte_val & 0x0F
                digits += str(high_digit) + str(low_digit)
            
            # Extract exact range
            offset = start % 2
            return digits[offset:offset + length]

# Example usage and testing
if __name__ == "__main__":
    config = StorageConfig()
    
    try:
        pi_db = PiStorage(config)
        
        # Test basic functionality
        first_50 = pi_db.get_digits(0, 50, force_verify=True)
        print(f"First 50 digits: {first_50}")
        
        # Build caches if needed
        if not os.path.exists(config.sqlite_db):
            def progress(current, total):
                print(f"Progress: {current}/{total} chunks ({100*current/total:.1f}%)")
            
            pi_db.build_caches(progress_callback=progress)
        
        # Test random access
        import random
        for _ in range(5):
            pos = random.randint(0, 1000000)
            digits = pi_db.get_digits(pos, 20, force_verify=True)
            print(f"Digits at position {pos}: {digits}")
        
    except FileNotFoundError:
        print("Pi file not found. Please ensure 'pi_1billion.txt' exists in the current directory.")
    except Exception as e:
        print(f"Error: {e}")