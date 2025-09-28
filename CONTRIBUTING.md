# Contributing to Math Constants Storage System

🎉 Thank you for considering contributing to the Math Constants Storage System! We welcome contributions from everyone.

## 🤝 How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear description** of the problem
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Docker version, etc.)
- **Relevant logs** or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear description** of the enhancement
- **Use case** explaining why this would be useful
- **Possible implementation** approach if you have ideas

### Code Contributions

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Ensure** all tests pass
6. **Commit** your changes with clear messages
7. **Push** to your fork
8. **Create** a Pull Request

## 🛠️ Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/math-constants-storage.git
cd math-constants-storage

# Copy environment file
cp .env.example .env

# Start development environment
./scripts/start.sh

# Run tests
docker-compose exec math-constants-api pytest
```

## 📋 Code Style Guidelines

### Python Code Style
- Follow **PEP 8** style guidelines
- Use **type hints** for all functions
- Write **docstrings** for classes and functions
- Keep **line length** under 88 characters
- Use **descriptive variable names**

### Example:
```python
def get_digits(self, start: int, length: int, verify: bool = False) -> str:
    """
    Retrieve digits from mathematical constant.
    
    Args:
        start: Starting position (0-based)
        length: Number of digits to retrieve
        verify: Whether to verify against original file
        
    Returns:
        String of digits
        
    Raises:
        CorruptionError: If data corruption detected
    """
    pass
```

### API Design
- Use **clear, descriptive endpoint names**
- Follow **RESTful conventions**
- Include **comprehensive error handling**
- Provide **detailed response models**

### Testing
- Write **unit tests** for all new functions
- Include **integration tests** for API endpoints
- Test **error conditions** and edge cases
- Maintain **minimum 80% code coverage**

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_storage.py

# Run tests in Docker
docker-compose exec math-constants-api pytest
```

## 📁 Project Structure

```
app/
├── storage/           # Core storage implementations
├── api/              # FastAPI endpoints and models  
├── core/             # Configuration and utilities
└── utils/            # Helper functions

tests/
├── test_storage.py   # Storage layer tests
├── test_api.py       # API endpoint tests
└── conftest.py       # Test configuration
```

## 🚀 Adding New Mathematical Constants

To add support for a new mathematical constant:

1. **Update configuration** in `app/core/config.py`
2. **Add file path** to environment variables
3. **Create storage instance** in main application
4. **Add API endpoints** for the new constant
5. **Write tests** for new functionality
6. **Update documentation**

Example for adding τ (tau):
```python
# In .env.example
TAU_FILE_PATH=/app/data/tau_digits.txt
TAU_SQLITE_DB=/app/data/tau_chunks.db
TAU_BINARY_FILE=/app/data/tau_binary.dat
```

## 📚 Documentation

- Update **README.md** for user-facing changes
- Update **API.md** for new endpoints
- Add **inline comments** for complex logic
- Update **CHANGELOG.md** for releases

## 🔍 Code Review Process

1. **Automated checks** must pass (tests, linting)
2. **Manual review** by maintainers
3. **Discussion** of implementation approach
4. **Approval** before merging

### What We Look For:
- **Correctness** of implementation
- **Performance** considerations
- **Security** implications
- **Maintainability** of code
- **Test coverage** of changes

## 🎯 Areas Needing Contribution

- **Performance optimizations** for large datasets
- **Additional mathematical constants** support
- **Frontend development** for web interface
- **Documentation improvements**
- **Test coverage** expansion
- **Docker optimizations**
- **CI/CD pipeline** enhancements

## 📝 Commit Message Guidelines

Use clear, descriptive commit messages:

```
feat: add support for tau mathematical constant
fix: resolve corruption detection in binary cache
docs: update API documentation for new endpoints
test: add integration tests for search functionality
refactor: optimize SQLite query performance
```

Prefix types:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

## 🤔 Questions?

- Check existing **GitHub Issues**
- Start a **GitHub Discussion**
- Review the **documentation**
- Ask in **Pull Request** comments

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make this project better! 🙏