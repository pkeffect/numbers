"""
Binary Source - Space-efficient binary storage.
"""

import os
from typing import Optional


class BinarySource:
    """Source for reading from binary packed storage."""
    
    def __init__(self, binary_path: str):
        self.binary_path = binary_path
        self._file_handle: Optional[object] = None
    
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
    
    def close(self):
        """Close file handle if open"""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None
    
    def __del__(self):
        """Cleanup file handle on deletion"""
        self.close()