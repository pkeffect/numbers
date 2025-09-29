# 🔢 Math Constants Storage System

High-performance, triple-redundancy storage system for accessing billions of digits of mathematical constants (π, φ, e, √2, and more) with FastAPI backend, multi-constant support, and accuracy-first design.

## ✨ Features

- **Multi-Constant Support**: Simultaneously manage 12 different mathematical constants
- **Triple Redundancy**: Original file + SQLite chunks + Binary cache
- **Smart Cache Management**: Automatically skips already-built caches
- **Accuracy First**: Automatic verification and corruption detection
- **High Performance**: Optimized for random access to billions of digits
- **Hot Reloading**: Development-friendly Docker setup
- **API Ready**: RESTful endpoints with automatic documentation
- **LLM Integration**: Clean JSON responses for AI/ML applications

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd math-constants-storage

# Copy environment configuration
cp .env.example .env

# Place your math constant files in data/ directory
# Expected filenames: pi_digits.txt, e_digits.txt, phi_digits.txt, etc.

# Start the development environment
docker-compose up --build
```

## 📊 Supported Mathematical Constants

| Constant | Symbol | Filename | Description |
|----------|---------|----------|-------------|
| Pi | π | `pi_digits.txt` | Ratio of circumference to diameter |
| Euler's number | e | `e_digits.txt` | Base of natural logarithm |
| Golden Ratio | φ | `phi_digits.txt` | (1 + √5) / 2 |
| Square Root of 2 | √2 | `sqrt2_digits.txt` | √2 |
| Square Root of 3 | √3 | `sqrt3_digits.txt` | √3 |
| Catalan | G | `catalan_digits.txt` | Catalan constant |
| Euler-Mascheroni | γ | `eulers_digits.txt` | Euler-Mascheroni constant |
| Lemniscate | ϖ | `lemniscate_digits.txt` | Lemniscate constant |
| Natural log of 2 | ln(2) | `log2_digits.txt` | Natural logarithm of 2 |
| Natural log of 3 | ln(3) | `log3_digits.txt` | Natural logarithm of 3 |
| Natural log of 10 | ln(10) | `log10_digits.txt` | Natural logarithm of 10 |
| Apéry's constant | ζ(3) | `zeta3_digits.txt` | Riemann zeta function ζ(3) |

## 🔧 API Endpoints

### **Multi-Constant Endpoints**

#### Get Available Constants
```bash
GET /constants
```
Returns list of all available mathematical constants with their status.

#### Get Constant Status
```bash
GET /constants/{constant_id}/status
```
Get detailed status for a specific constant (file size, cache status, etc.).

#### Health Check
```bash
GET /health
```
Multi-constant aware health check showing cache status for all constants.

### **Digit Retrieval**

#### Get Digits from Specific Constant
```bash
GET /digits/{constant_id}?start=0&length=50
```
Retrieve digits from any mathematical constant.

**Examples:**
```bash
# Get first 50 digits of Pi
curl "http://localhost:8000/digits/pi?start=0&length=50"

# Get first 50 digits of Euler's number
curl "http://localhost:8000/digits/e?start=0&length=50"

# Get digits from Golden Ratio with verification
curl "http://localhost:8000/digits/phi?start=1000&length=100&verify=true"
```

#### Random Digits
```bash
GET /random/{constant_id}?length=10&seed=42
```
Get random digits from any mathematical constant.

### **Search and Analysis**

#### Search for Sequence
```bash
GET /search/{constant_id}?sequence=123456
```
Find occurrences of a digit sequence in any constant.

**Example:**
```bash
# Find your birthday in Pi
curl "http://localhost:8000/search/pi?sequence=19851201"

# Find pattern in Euler's number
curl "http://localhost:8000/search/e?sequence=271828"
```

#### Statistical Analysis
```bash
GET /stats/{constant_id}?start=0&sample_size=100000
```
Get digit frequency analysis for any constant.

### **Cache Management (Admin)**

#### Build Cache for Specific Constant
```bash
POST /admin/build-cache/{constant_id}
```
Build cache for a single mathematical constant.

**Examples:**
```bash
# Build cache for Euler's number
curl -X POST http://localhost:8000/admin/build-cache/e

# Force rebuild Pi cache
curl -X POST "http://localhost:8000/admin/build-cache/pi?force_rebuild=true"
```

#### Build All Caches
```bash
POST /admin/build-all-caches?force_rebuild=false
```
Build caches for ALL available constants. **Automatically skips already-cached constants.**

**Examples:**
```bash
# Build all caches (skips already-cached)
curl -X POST http://localhost:8000/admin/build-all-caches

# Force rebuild all caches (including already-cached)
curl -X POST "http://localhost:8000/admin/build-all-caches?force_rebuild=true"
```

#### Verify Data Integrity
```bash
POST /admin/verify/{constant_id}?sample_count=10
```
Verify data integrity for a specific constant.

### **Documentation**
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)
- `GET /` - API root with status information

## 📁 Project Structure

```
math-constants-storage/
├── app/                          # Application source code
│   ├── main.py                  # FastAPI application (multi-constant support)
│   ├── storage/                 # Storage layer
│   │   ├── manager.py          # Single constant manager
│   │   ├── multi_manager.py    # Multi-constant manager (NEW)
│   │   ├── file_source.py      # Original file access
│   │   ├── sqlite_source.py    # SQLite chunked storage
│   │   └── binary_source.py    # Binary packed storage
│   ├── api/                     # API endpoints and models
│   │   ├── models/
│   │   │   ├── requests.py     # Request models
│   │   │   └── responses.py    # Response models
│   ├── core/                    # Core utilities
│   │   ├── config.py           # Configuration
│   │   ├── constants.py        # Mathematical constants definitions
│   │   └── exceptions.py       # Custom exceptions
│   └── utils/                   # Helper functions
├── data/                        # Math constant data files (gitignored)
├── logs/                        # Application logs (gitignored)
├── tests/                       # Test suite
└── docker/                      # Docker configuration
```

## 🐳 Docker Development

```bash
# Start basic development environment
docker-compose up

# Start with SQLite browser for debugging
docker-compose --profile debug up

# View logs
docker-compose logs -f math-constants-api

# Rebuild containers
docker-compose up --build

# Stop all services
docker-compose down
```

## 🔒 Data Integrity

### Triple Verification System
1. **Original File**: Source of truth, never modified
2. **SQLite Chunks**: Fast access with MD5 checksums
3. **Binary Cache**: Space-efficient with built-in verification

### Automatic Safeguards
- Checksums on all cached data
- Cross-source validation every 100th request
- Startup integrity verification
- Corruption detection and fallback
- Smart cache building (skips complete caches)

## ⚙️ Configuration

Key environment variables (see `.env.example`):

```bash
# Primary Math Constant (Pi)
PI_FILE_PATH=/app/data/pi_digits.txt
PI_SQLITE_DB=/app/data/pi_chunks.db
PI_BINARY_FILE=/app/data/pi_binary.dat

# Additional constants follow same pattern
E_FILE_PATH=/app/data/e_digits.txt
PHI_FILE_PATH=/app/data/phi_digits.txt
# ... etc for all 12 constants

# Storage Configuration
CHUNK_SIZE=10000
VERIFY_EVERY=100

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## 🧪 Testing

```bash
# Run tests
docker-compose exec math-constants-api pytest

# Run with coverage
docker-compose exec math-constants-api pytest --cov=app

# Run specific test file
docker-compose exec math-constants-api pytest tests/test_storage.py
```

## 🚀 Performance

- **Random Access**: O(1) lookup to any position
- **Memory Efficient**: Handles multi-GB files without loading into memory
- **Cached Queries**: SQLite index for frequently accessed ranges
- **Parallel Safe**: Thread-safe storage operations
- **Smart Caching**: Automatic detection of existing caches

## 🤖 LLM Integration Examples

```python
import requests

# List available constants
response = requests.get("http://localhost:8000/constants")
constants = response.json()

# Search for patterns in multiple constants
for constant in ["pi", "e", "phi"]:
    result = requests.get(f"http://localhost:8000/search/{constant}?sequence=123456")
    print(f"{constant}: {result.json()}")

# Get random digits for creative applications
response = requests.get("http://localhost:8000/random/pi?length=100&seed=42")

# Statistical analysis for research
response = requests.get("http://localhost:8000/stats/e?start=1000000&sample_size=100000")
```

## 📊 Usage Examples

### Check System Status
```bash
# Overall health
curl http://localhost:8000/health

# List all constants
curl http://localhost:8000/constants

# Check specific constant
curl http://localhost:8000/constants/pi/status
```

### Build Caches for All Constants
```bash
# Build all (skips already-cached, like Pi)
curl -X POST http://localhost:8000/admin/build-all-caches

# Monitor progress in logs
docker-compose logs -f math-constants-api
```

### Access Multiple Constants
```bash
# Pi digits
curl "http://localhost:8000/digits/pi?start=0&length=100"

# Euler's number
curl "http://localhost:8000/digits/e?start=0&length=100"

# Golden ratio
curl "http://localhost:8000/digits/phi?start=0&length=100"
```

## 🔮 Future Roadmap

- [ ] Advanced pattern recognition with ML
- [ ] GraphQL API support
- [ ] Real-time WebSocket subscriptions
- [ ] Distributed storage across multiple nodes
- [ ] Redis caching layer
- [ ] Advanced mathematical sequence analysis
- [ ] Web-based visualization interface
- [ ] Bulk operations API

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🙏 Acknowledgments

- Mathematical constants computed using high-precision algorithms
- Built with FastAPI, SQLite, and Docker
- Inspired by the beauty of mathematical constants
- Community contributions and feedback

## 📞 Support

- 📚 [Full Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)
- 📧 [Email Support](mailto:support@mathconstants.dev)

## 🎯 Key Changes from v1.0

- ✅ **Multi-constant support** - Manage 12 constants simultaneously
- ✅ **Smart cache building** - Automatically skips already-built caches
- ✅ **Enhanced API** - New endpoints for multi-constant operations
- ✅ **Better health checks** - Multi-constant aware status reporting
- ✅ **Improved error handling** - More informative error messages
- ✅ **Bulk operations** - Build all caches with one command

---

**Note**: This system is designed for educational, research, and creative applications. Ensure you have proper rights to use any mathematical constant datasets.