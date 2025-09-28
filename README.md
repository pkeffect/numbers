# 🔢 Math Constants Storage System

High-performance, triple-redundancy storage system for accessing billions of digits of mathematical constants (π, φ, e, √2, etc.) with FastAPI backend and accuracy-first design.

## ✨ Features

- **Triple Redundancy**: Original file + SQLite chunks + Binary cache
- **Accuracy First**: Automatic verification and corruption detection
- **High Performance**: Optimized for random access to billions of digits
- **Hot Reloading**: Development-friendly Docker setup
- **Future-Proof**: Designed for π, φ, e, √2, and other mathematical constants
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
# Expected filenames: pi_digits.txt, phi_digits.txt, e_digits.txt, etc.

# Start the development environment
./scripts/start.sh
```

## 📁 Project Structure

```
math-constants-storage/
├── app/                    # Application source code
│   ├── main.py            # FastAPI application entry point
│   ├── storage/           # Storage layer (file, SQLite, binary)
│   ├── api/               # API endpoints and models
│   ├── core/              # Configuration and core utilities
│   └── utils/             # Helper functions
├── data/                  # Math constant data files (gitignored)
├── logs/                  # Application logs (gitignored)
├── frontend/              # Optional web interface
├── tests/                 # Test suite
├── scripts/               # Utility scripts
└── docker/               # Docker configuration
```

## 🔧 API Endpoints

### Core Endpoints
- `GET /digits` - Retrieve digits from any position
- `GET /search` - Find sequences (birthdays, phone numbers, etc.)
- `GET /stats` - Statistical analysis of digit distribution
- `GET /random` - Get random digits from mathematical constants
- `GET /health` - System health and integrity check

### Admin Endpoints
- `POST /admin/build-caches` - Build SQLite and binary caches
- `POST /admin/verify` - Verify data integrity across all sources

### Documentation
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

## 🐳 Docker Development

```bash
# Start basic development environment
docker-compose up

# Start with SQLite browser for debugging
docker-compose --profile debug up

# Start with frontend for testing
docker-compose --profile frontend up

# Rebuild containers
./scripts/rebuild.sh
```

## 📊 Supported Mathematical Constants

| Constant | Symbol | Filename | Description |
|----------|---------|----------|-------------|
| Catalan | G | `catalan_digits.txt` | Catalan constant |
| Euler's number | e | `e_digits.txt` | Base of natural logarithm |
| Euler-Mascheroni | γ | `eulers_digits.txt` | Euler-Mascheroni constant |
| Lemniscate | ϖ | `lemniscate_digits.txt` | Lemniscate constant |
| Natural log of 10 | ln(10) | `log10_digits.txt` | Natural logarithm of 10 |
| Natural log of 2 | ln(2) | `log2_digits.txt` | Natural logarithm of 2 |
| Natural log of 3 | ln(3) | `log3_digits.txt` | Natural logarithm of 3 |
| Golden Ratio | φ | `phi_digits.txt` | (1 + √5) / 2 |
| Pi | π | `pi_digits.txt` | Ratio of circumference to diameter |
| Square Root of 2 | √2 | `sqrt2_digits.txt` | √2 |
| Square Root of 3 | √3 | `sqrt3_digits.txt` | √3 |
| Apéry's constant | ζ(3) | `zeta3_digits.txt` | Riemann zeta function ζ(3) |

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

## ⚙️ Configuration

Key environment variables (see `.env.example`):

```bash
# Math Constants File Paths
PI_FILE_PATH=/app/data/pi_digits.txt
PHI_FILE_PATH=/app/data/phi_digits.txt
E_FILE_PATH=/app/data/e_digits.txt

# Storage Configuration
CHUNK_SIZE=10000
VERIFY_EVERY=100

# API Keys (for LLM integrations)
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
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

## 🤖 LLM Integration Examples

```python
# Search for patterns
response = requests.get("http://localhost:8000/search?sequence=123456")

# Get random digits for creative applications
response = requests.get("http://localhost:8000/random?length=100&seed=42")

# Statistical analysis for research
response = requests.get("http://localhost:8000/stats?start=1000000&sample_size=100000")
```

## 🔮 Future Roadmap

- [ ] Support for additional mathematical constants
- [ ] Advanced pattern recognition with ML
- [ ] GraphQL API
- [ ] Real-time WebSocket subscriptions
- [ ] Distributed storage across multiple nodes
- [ ] Advanced caching with Redis
- [ ] Mathematical sequence analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Mathematical constants computed using high-precision algorithms
- Built with FastAPI, SQLite, and Docker
- Inspired by the beauty of mathematical constants

## 📞 Support

- 📚 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)

---

**Note**: This system is designed for educational, research, and creative applications. Ensure you have proper rights to use any mathematical constant datasets.