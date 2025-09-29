"""
File Source - Original file access for mathematical constants.
"""

import os
from typing import Optional
from app.core.exceptions import StorageError


class FileSource:
    """Source for reading from original mathematical constant files."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._file_handle: Optional[object] = None
        self._file_size: Optional[int] = None
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Math constant file not found: {filepath}")
        
        # Validate file is readable
        try:
            with open(filepath, 'r') as f:
                # Try to read first few characters to validate
                test_read = f.read(10)
                if not test_read:
                    raise StorageError(f"File appears to be empty: {filepath}")
        except Exception as e:
            raise StorageError(f"Cannot read file {filepath}: {e}")
    
    def get(self, start: int, length: int) -> str:
        """Get content from original file using seek"""
        if start < 0:
            raise ValueError("Start position cannot be negative")
        if length < 1:
            raise ValueError("Length must be positive")
            
        try:
            # Use context manager for better resource handling
            with open(self.filepath, 'r') as f:
                f.seek(start)
                content = f.read(length)
                
                if not content and start == 0:
                    raise StorageError("File appears to be empty")
                
                return content
                
        except IOError as e:
            raise StorageError(f"Error reading from file: {e}")
        except Exception as e:
            raise StorageError(f"Unexpected error reading file: {e}")
    
    def get_file_size(self) -> int:
        """Get total file size in characters"""
        if self._file_size is None:
            try:
                self._file_size = os.path.getsize(self.filepath)
            except OSError as e:
                raise StorageError(f"Cannot get file size: {e}")
        return self._file_size
    
    def get_line_count(self) -> int:
        """Get total number of lines in the file"""
        try:
            with open(self.filepath, 'r') as f:
                return sum(1 for line in f)
        except Exception as e:
            raise StorageError(f"Cannot count lines: {e}")
    
    def validate_content(self, max_check_chars: int = 1000) -> dict:
        """Validate file content and return analysis"""
        try:
            with open(self.filepath, 'r') as f:
                content = f.read(max_check_chars)
            
            # Count different character types
            digits = sum(1 for c in content if c.isdigit())
            decimal_points = content.count('.')
            whitespace = sum(1 for c in content if c.isspace())
            other_chars = len(content) - digits - decimal_points - whitespace
            
            # Analyze structure
            has_decimal = '.' in content
            starts_with_digit = content and content[0].isdigit()
            
            return {
                'total_chars_checked': len(content),
                'digit_count': digits,
                'decimal_points': decimal_points,
                'whitespace_count': whitespace,
                'other_chars': other_chars,
                'digit_percentage': (digits / len(content)) * 100 if content else 0,
                'has_decimal_point': has_decimal,
                'starts_with_digit': starts_with_digit,
                'appears_valid': digits > len(content) * 0.8  # At least 80% digits
            }
            
        except Exception as e:
            return {'error': str(e), 'appears_valid': False}
    
    def get_sample_content(self, start: int = 0, length: int = 100) -> str:
        """Get a sample of content for inspection"""
        try:
            return self.get(start, min(length, self.get_file_size() - start))
        except Exception as e:
            raise StorageError(f"Cannot get sample content: {e}")
    
    def search_in_file(self, pattern: str, max_results: int = 100) -> list:
        """Search for a pattern in the file and return positions"""
        positions = []
        
        try:
            with open(self.filepath, 'r') as f:
                position = 0
                chunk_size = 1000000  # 1MB chunks
                overlap = len(pattern) - 1
                
                while len(positions) < max_results:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Find all occurrences in this chunk
                    start_pos = 0
                    while start_pos < len(chunk):
                        found_pos = chunk.find(pattern, start_pos)
                        if found_pos == -1:
                            break
                        
                        positions.append(position + found_pos)
                        if len(positions) >= max_results:
                            break
                        
                        start_pos = found_pos + 1
                    
                    position += len(chunk) - overlap
                    if len(chunk) < chunk_size:
                        break
                    
                    # Seek back for overlap
                    f.seek(position)
                    
        except Exception as e:
            raise StorageError(f"Error searching file: {e}")
        
        return positions
    
    def get_file_info(self) -> dict:
        """Get comprehensive file information"""
        try:
            stat = os.stat(self.filepath)
            validation = self.validate_content()
            
            return {
                'filepath': self.filepath,
                'exists': True,
                'size_bytes': stat.st_size,
                'readable': True,
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime,
                'validation': validation
            }
        except Exception as e:
            return {
                'filepath': self.filepath,
                'exists': os.path.exists(self.filepath),
                'error': str(e)
            }
    
    def close(self):
        """Close file handle if open (for compatibility)"""
        # This implementation uses context managers, so no persistent handle
        pass
    
    def __del__(self):
        """Cleanup file handle on deletion (for compatibility)"""
        self.close()