"""
SQLite Source - Fast chunked access with checksums.
"""

import sqlite3
import hashlib
from typing import List, Tuple
from app.core.exceptions import CorruptionError


class SQLiteSource:
    """Source for reading from SQLite chunked storage."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize database tables"""
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS math_chunks (
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
            ON math_chunks(start_position, end_position)
        ''')
        
        self.conn.commit()
    
    def store_chunk(self, chunk_id: int, start_pos: int, digits: str):
        """Store a chunk with checksum"""
        end_pos = start_pos + len(digits)
        checksum = hashlib.md5(digits.encode()).hexdigest()
        
        self.conn.execute('''
            INSERT OR REPLACE INTO math_chunks 
            (chunk_id, start_position, end_position, digits, checksum)
            VALUES (?, ?, ?, ?, ?)
        ''', (chunk_id, start_pos, end_pos, digits, checksum))
        
        self.conn.commit()
    
    def get(self, start: int, length: int) -> str:
        """Get digits from database, potentially spanning multiple chunks"""
        end = start + length
        
        cursor = self.conn.execute('''
            SELECT start_position, end_position, digits, checksum
            FROM math_chunks
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
    
    def has_data(self) -> bool:
        """Check if the database has any data"""
        try:
            cursor = self.conn.execute('SELECT COUNT(*) FROM math_chunks')
            count = cursor.fetchone()[0]
            return count > 0
        except:
            return False
    
    def get_chunk_count(self) -> int:
        """Get total number of chunks stored"""
        try:
            cursor = self.conn.execute('SELECT COUNT(*) FROM math_chunks')
            return cursor.fetchone()[0]
        except:
            return 0
    
    def get_coverage_range(self) -> tuple:
        """Get the range of positions covered by stored chunks"""
        try:
            cursor = self.conn.execute('''
                SELECT MIN(start_position), MAX(end_position) 
                FROM math_chunks
            ''')
            result = cursor.fetchone()
            if result and result[0] is not None:
                return result
            else:
                return (0, 0)
        except:
            return (0, 0)
    
    def verify_all_chunks(self) -> List[dict]:
        """Verify checksums of all stored chunks"""
        verification_results = []
        
        try:
            cursor = self.conn.execute('''
                SELECT chunk_id, start_position, end_position, digits, checksum
                FROM math_chunks
                ORDER BY start_position
            ''')
            
            for chunk_id, start_pos, end_pos, digits, stored_checksum in cursor:
                calculated_checksum = hashlib.md5(digits.encode()).hexdigest()
                is_valid = calculated_checksum == stored_checksum
                
                verification_results.append({
                    'chunk_id': chunk_id,
                    'start_position': start_pos,
                    'end_position': end_pos,
                    'is_valid': is_valid,
                    'stored_checksum': stored_checksum,
                    'calculated_checksum': calculated_checksum
                })
                
                if not is_valid:
                    print(f"❌ Chunk {chunk_id} failed verification at position {start_pos}")
        
        except Exception as e:
            print(f"Error during chunk verification: {e}")
        
        return verification_results
    
    def clear_all_data(self):
        """Clear all stored chunks (use with caution)"""
        try:
            self.conn.execute('DELETE FROM math_chunks')
            self.conn.commit()
            print("✅ All chunks cleared from database")
        except Exception as e:
            print(f"❌ Error clearing chunks: {e}")
    
    def get_database_info(self) -> dict:
        """Get information about the database"""
        try:
            # Get table info
            cursor = self.conn.execute("PRAGMA table_info(math_chunks)")
            columns = cursor.fetchall()
            
            # Get chunk count and coverage
            chunk_count = self.get_chunk_count()
            coverage_start, coverage_end = self.get_coverage_range()
            
            # Get database file size
            cursor = self.conn.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor = self.conn.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            db_size = page_count * page_size
            
            return {
                'db_path': self.db_path,
                'chunk_count': chunk_count,
                'coverage_start': coverage_start,
                'coverage_end': coverage_end,
                'total_coverage': coverage_end - coverage_start if coverage_end > coverage_start else 0,
                'database_size_bytes': db_size,
                'columns': [col[1] for col in columns]
            }
        except Exception as e:
            return {'error': str(e)}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup connection on deletion"""
        self.close()