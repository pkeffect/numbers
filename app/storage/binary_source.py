"""
Binary Source - Space-efficient binary storage.
"""

import os
from typing import Optional
from app.core.exceptions import StorageError


class BinarySource:
    """Source for reading from binary packed storage."""
    
    def __init__(self, binary_path: str):
        self.binary_path = binary_path
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Ensure the directory for the binary file exists"""
        directory = os.path.dirname(self.binary_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def store_chunk(self, start_pos: int, digits: str):
        """Store digits in binary format (4 bits per digit)"""
        if not digits.isdigit():
            raise ValueError("Can only store digit characters")
        
        try:
            # Calculate file position for this chunk
            byte_position = start_pos // 2
            
            # Open file in read+write mode, create if doesn't exist
            mode = 'r+b' if os.path.exists(self.binary_path) else 'w+b'
            
            with open(self.binary_path, mode) as f:
                # Seek to the correct position
                f.seek(byte_position)
                
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
                
                f.write(binary_data)
                f.flush()
                
        except Exception as e:
            raise StorageError(f"Error storing binary chunk: {e}")
    
    def get(self, start: int, length: int) -> str:
        """Get digits from binary file"""
        if not os.path.exists(self.binary_path):
            raise FileNotFoundError("Binary cache not built yet")
        
        if start < 0:
            raise ValueError("Start position cannot be negative")
        if length < 1:
            raise ValueError("Length must be positive")
        
        try:
            with open(self.binary_path, 'rb') as f:
                # Calculate byte positions
                start_byte = start // 2
                # Need extra byte if we start or end on odd position
                end_pos = start + length
                end_byte = (end_pos + 1) // 2
                
                f.seek(start_byte)
                bytes_to_read = end_byte - start_byte
                binary_data = f.read(bytes_to_read)
                
                if not binary_data:
                    raise StorageError(f"No data available at position {start}")
                
                # Unpack bytes to digits
                digits = ""
                for byte_val in binary_data:
                    high_digit = byte_val >> 4
                    low_digit = byte_val & 0x0F
                    digits += str(high_digit) + str(low_digit)
                
                # Extract exact range accounting for odd start positions
                offset = start % 2
                result = digits[offset:offset + length]
                
                if len(result) != length:
                    raise StorageError(f"Retrieved {len(result)} digits, expected {length}")
                
                return result
                
        except FileNotFoundError:
            raise FileNotFoundError("Binary cache file not found")
        except Exception as e:
            raise StorageError(f"Error reading from binary file: {e}")
    
    def append_digits(self, digits: str):
        """Append digits to the end of the binary file"""
        if not digits.isdigit():
            raise ValueError("Can only store digit characters")
        
        try:
            with open(self.binary_path, 'ab') as f:
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
                
                f.write(binary_data)
                f.flush()
                
        except Exception as e:
            raise StorageError(f"Error appending to binary file: {e}")
    
    def get_file_size(self) -> int:
        """Get binary file size in bytes"""
        try:
            if os.path.exists(self.binary_path):
                return os.path.getsize(self.binary_path)
            return 0
        except Exception as e:
            raise StorageError(f"Cannot get binary file size: {e}")
    
    def get_digit_count(self) -> int:
        """Get approximate number of digits stored (2 per byte)"""
        return self.get_file_size() * 2
    
    def verify_integrity(self, original_digits: str, start_pos: int = 0) -> bool:
        """Verify binary data matches original digits"""
        try:
            stored_digits = self.get(start_pos, len(original_digits))
            return stored_digits == original_digits
        except Exception:
            return False
    
    def clear_file(self):
        """Clear the binary file (use with caution)"""
        try:
            if os.path.exists(self.binary_path):
                os.remove(self.binary_path)
                print(f"✅ Binary file cleared: {self.binary_path}")
            else:
                print(f"ℹ️  Binary file doesn't exist: {self.binary_path}")
        except Exception as e:
            raise StorageError(f"Error clearing binary file: {e}")
    
    def get_file_info(self) -> dict:
        """Get information about the binary file"""
        try:
            if not os.path.exists(self.binary_path):
                return {
                    'filepath': self.binary_path,
                    'exists': False,
                    'size_bytes': 0,
                    'estimated_digits': 0
                }
            
            stat = os.stat(self.binary_path)
            size_bytes = stat.st_size
            
            return {
                'filepath': self.binary_path,
                'exists': True,
                'size_bytes': size_bytes,
                'estimated_digits': size_bytes * 2,
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime,
                'compression_ratio': 0.5  # 4 bits per digit vs 8 bits per char
            }
        except Exception as e:
            return {
                'filepath': self.binary_path,
                'exists': False,
                'error': str(e)
            }
    
    def sample_data(self, start: int = 0, length: int = 20) -> dict:
        """Get a sample of data for debugging"""
        try:
            if not os.path.exists(self.binary_path):
                return {'error': 'File does not exist'}
            
            # Read raw bytes
            with open(self.binary_path, 'rb') as f:
                f.seek(start // 2)
                raw_bytes = f.read((length + 1) // 2)
            
            # Convert to hex for debugging
            hex_data = raw_bytes.hex()
            
            # Get decoded digits
            try:
                digits = self.get(start, min(length, self.get_digit_count() - start))
            except:
                digits = "Error decoding"
            
            return {
                'start_position': start,
                'requested_length': length,
                'raw_bytes_hex': hex_data,
                'decoded_digits': digits,
                'byte_count': len(raw_bytes)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def close(self):
        """Close file handle if open (for compatibility)"""
        # This implementation uses context managers, so no persistent handle
        pass
    
    def __del__(self):
        """Cleanup file handle on deletion"""
        self.close()