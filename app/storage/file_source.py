"""
File Source - Original file access for mathematical constants.
"""

import os
from typing import Optional


class FileSource:
    """Source for reading from original mathematical constant files."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._file_handle: Optional[object] = None
        self._file_size: Optional[int] = None
        
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
    
    def close(self):
        """Close file handle if open"""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
    
    def __del__(self):
        """Cleanup file handle on deletion"""
        self.close()