# 🔢 Math Constants Storage System

High-performance, triple-redundancy storage system for accessing billions of digits of mathematical constants (π, φ, e, √2, and more) with FastAPI backend, dedicated endpoints per constant, and accuracy-first design.

## ✨ Features

- **12 Mathematical Constants**: Pi, Euler's number, Golden ratio, Square roots, Logarithms, and more
- **Dedicated Endpoints**: Each constant has its own clean API namespace (`/pi/*`, `/e/*`, etc.)
- **Triple Redundancy**: Original file + SQLite chunks + Binary cache
- **Smart Cache Management**: Automatically skips already-built caches
- **Accuracy First**: Automatic verification and corruption detection
- **High Performance**: Optimized for random access to billions of digits
- **Modular Architecture**: Clean separation with 16 focused router files
- **Hot Reloading**: Development-friendly Docker setup
- **Backward Compatible**: Legacy parameterized endpoints still work
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

| Constant | Symbol | Endpoint | Filename | Description |
|----------|---------|----------|----------|-------------|
| Pi | π | `/pi/*` | `pi_digits.txt` | Ratio of circumference to diameter |
| Euler's number | e | `/e/*` | `e_digits.txt` | Base of natural logarithm |
| Golden Ratio | φ | `/phi/*` | `phi_digits.txt` | (1 + √5) / 2 |
| Square Root of 2 | √2 | `/sqrt2/*` | `sqrt2_digits.txt` | √2 |
| Square Root of 3 | √3 | `/sqrt3/*` | `sqrt3_digits.txt` | √3 |
| Catalan | G | `/catalan/*` | `catalan_digits.txt` | Catalan constant |
| Euler-Mascheroni | γ | `/eulers/*` | `eulers_digits.txt` | Euler-Mascheroni constant |
| Lemniscate | ϖ | `/lemniscate/*` | `lemniscate_digits.txt` | Lemniscate constant |
| Natural log of 2 | ln(2) | `/log2/*` | `log2_digits.txt` | Natural logarithm of 2 |
| Natural log of 3 | ln(3) | `/log3/*` | `log3_digits.txt` | Natural logarithm of 3 |
| Natural log of 10 | ln(10) | `/log10/*` | `log10_digits.txt` | Natural logarithm of 10 |
| Apéry's constant | ζ(3) | `/zeta3/*` | `zeta3_digits.txt` | Riemann zeta function ζ(3) |

## 🔧 API Endpoints

### **General Endpoints**

```bash
GET  /                    # API root with system info
GET  /health              # System health check
GET  /constants           # List all constants with status
```

### **Per-Constant Endpoints** (Pattern for all 12 constants)

Each constant has 7 dedicated endpoints:

```bash
GET  /{constant}/status        # Status and cache information
GET  /{constant}/digits        # Retrieve digits from position
GET  /{constant}/search        # Search for digit sequences
GET  /{constant}/stats         # Statistical analysis
GET  /{constant}/random        # Get random digits
POST /{constant}/build-cache   # Build SQLite and binary cache
POST /{constant}/verify        # Verify data integrity
```

**Example for Pi (π):**
```bash
GET  /pi/status
GET  /pi/digits?start=0&length=50
GET  /pi/search?sequence=123456
GET  /pi/stats?sample_size=10000
GET  /pi/random?length=20&seed=42
POST /pi/build-cache
POST /pi/verify?sample_count=5
```

### **Admin Endpoints**

```bash
POST /admin/build-all-caches   # Build caches for all constants
GET  /admin/status             # Administrative status
```

### **Legacy Endpoints** (Deprecated but still functional)

For backward compatibility, the old parameterized style still works:

```bash
GET  /digits/{constant_id}              # Use /{constant}/digits instead
GET  /search/{constant_id}              # Use /{constant}/search instead
GET  /stats/{constant_id}               # Use /{constant}/stats instead
GET  /random/{constant_id}              # Use /{constant}/random instead
POST /admin/build-cache/{constant_id}   # Use /{constant}/build-cache instead
POST /admin/verify/{constant_id}        # Use /{constant}/verify instead
```

### **Documentation**
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## 📁 Project Structure

```
math-constants-storage/
├── app/
│   ├── main.py                      # Application entry (60 lines)
│   ├── api/
│   │   ├── routers/                 # Modular routers (NEW!)
│   │   │   ├── __init__.py         # Router exports
│   │   │   ├── general.py          # Root, health, list
│   │   │   ├── admin.py            # Bulk operations
│   │   │   ├── legacy.py           # Backward compatibility
│   │   │   ├── pi.py               # Pi endpoints
│   │   │   ├── e.py                # Euler's number endpoints
│   │   │   ├── phi.py              # Golden ratio endpoints
│   │   │   ├── sqrt2.py            # √2 endpoints
│   │   │   ├── sqrt3.py            # √3 endpoints
│   │   │   ├── catalan.py          # Catalan constant endpoints
│   │   │   ├── eulers.py           # Euler-Mascheroni endpoints
│   │   │   ├── lemniscate.py       # Lemniscate endpoints
│   │   │   ├── log2.py             # ln(2) endpoints
│   │   │   ├── log3.py             # ln(3) endpoints
│   │   │   ├── log10.py            # ln(10) endpoints
│   │   │   └── zeta3.py            # Apéry's constant endpoints
│   │   └── models/
│   │       ├── requests.py         # Request models
│   │       └── responses.py        # Response models
│   ├── storage/
│   │   ├── manager.py              # Single constant manager
│   │   ├── multi_manager.py        # Multi-constant manager
│   │   ├── file_source.py          # Original file access
│   │   ├── sqlite_source.py        # SQLite chunked storage
│   │   └── binary_source.py        # Binary packed storage
│   ├── core/
│   │   ├── config.py               # Configuration
│   │   ├── constants.py            # Mathematical constants definitions
│   │   └── exceptions.py           # Custom exceptions
│   └── utils/                       # Helper functions
├── data/                            # Math constant data files (gitignored)
├── logs/                            # Application logs (gitignored)
├── tests/                           # Test suite
└── docker/                          # Docker configuration
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

# Get Pi digits
response = requests.get("http://localhost:8000/pi/digits?start=0&length=100")
pi_data = response.json()

# Search for birthday in multiple constants
for constant in ["pi", "e", "phi"]:
    result = requests.get(f"http://localhost:8000/{constant}/search?sequence=19851201")
    print(f"{constant}: {result.json()}")

# Get random digits for creative applications
response = requests.get("http://localhost:8000/pi/random?length=100&seed=42")

# Statistical analysis for research
response = requests.get("http://localhost:8000/e/stats?sample_size=100000")
```

## 📊 Usage Examples

### Check System Status
```bash
# Overall health
curl http://localhost:8000/health

# List all constants
curl http://localhost:8000/constants

# Check specific constant
curl http://localhost:8000/pi/status
```

### Build Caches for All Constants
```bash
# Build all (skips already-cached)
curl -X POST http://localhost:8000/admin/build-all-caches

# Force rebuild all
curl -X POST "http://localhost:8000/admin/build-all-caches?force_rebuild=true"

# Monitor progress in logs
docker-compose logs -f math-constants-api
```

### Access Multiple Constants
```bash
# Pi digits
curl "http://localhost:8000/pi/digits?start=0&length=100"

# Euler's number
curl "http://localhost:8000/e/digits?start=0&length=100"

# Golden ratio
curl "http://localhost:8000/phi/digits?start=0&length=100"

# Search for pattern in Pi
curl "http://localhost:8000/pi/search?sequence=123456"

# Get statistics for √2
curl "http://localhost:8000/sqrt2/stats?sample_size=50000"
```

## 🎯 What's New in v2.0

### Major Changes
- ✅ **Dedicated endpoints per constant** - Clean URLs like `/pi/digits` instead of `/digits/pi`
- ✅ **Modular router architecture** - 16 focused files instead of 1 monolithic main.py
- ✅ **Backward compatible** - Old parameterized endpoints still work (marked as deprecated)
- ✅ **Enhanced documentation** - Better organized Swagger UI with grouping by constant
- ✅ **Admin status endpoint** - Monitor cache status and system health
- ✅ **Improved error handling** - Better error messages and edge case handling

### Migration from v1.0
Old endpoints still work but are deprecated:
```bash
# Old style (still works)
curl "http://localhost:8000/digits/pi?start=0&length=50"

# New style (recommended)
curl "http://localhost:8000/pi/digits?start=0&length=50"
```

## 🔮 Future Roadmap

- [ ] Advanced pattern recognition with ML
- [ ] GraphQL API support
- [ ] Real-time WebSocket subscriptions for streaming digits
- [ ] Distributed storage across multiple nodes
- [ ] Redis caching layer for frequently accessed ranges
- [ ] Advanced mathematical sequence analysis
- [ ] Web-based visualization interface
- [ ] Comparison endpoints (compare patterns across constants)
- [ ] Export endpoints (download ranges in various formats)
- [ ] Rate limiting per constant
- [ ] Authentication and authorization
- [ ] Metadata endpoints (mathematical properties and fun facts)

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

---

**Note**: This system is designed for educational, research, and creative applications. Ensure you have proper rights to use any mathematical constant datasets.