"""
SQLite Source - Fast chunked access with checksums.
"""

import sqlite3
import hashlib
from typing import List, Tuple


class CorruptionError(Exception):
    """Raised when data corruption is detected"""
    pass


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
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup connection on deletion"""
        self.close()