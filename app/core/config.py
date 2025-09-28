"""
Configuration settings for the Math Constants Storage System.
"""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application Environment
    env: str = Field(default="development", description="Environment")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="info", description="Log level")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_workers: int = Field(default=1, description="Number of workers")
    api_title: str = Field(default="Math Constants API", description="API title")
    api_description: str = Field(
        default="High-accuracy API for accessing billions of digits of mathematical constants",
        description="API description"
    )
    api_version: str = Field(default="1.0.0", description="API version")

    # CORS Settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins"
    )
    cors_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE"],
        description="CORS allowed methods"
    )
    cors_headers: List[str] = Field(default=["*"], description="CORS allowed headers")

    # Directory Paths
    data_dir: str = Field(default="/app/data", description="Data directory")
    logs_dir: str = Field(default="/app/logs", description="Logs directory")

    # Math Constants File Paths
    catalan_file_path: str = Field(default="/app/data/catalan_digits.txt")
    e_file_path: str = Field(default="/app/data/e_digits.txt")
    eulers_file_path: str = Field(default="/app/data/eulers_digits.txt")
    lemniscate_file_path: str = Field(default="/app/data/lemniscate_digits.txt")
    log10_file_path: str = Field(default="/app/data/log10_digits.txt")
    log2_file_path: str = Field(default="/app/data/log2_digits.txt")
    log3_file_path: str = Field(default="/app/data/log3_digits.txt")
    phi_file_path: str = Field(default="/app/data/phi_digits.txt")
    pi_file_path: str = Field(default="/app/data/pi_digits.txt")
    sqrt2_file_path: str = Field(default="/app/data/sqrt2_digits.txt")
    sqrt3_file_path: str = Field(default="/app/data/sqrt3_digits.txt")
    zeta3_file_path: str = Field(default="/app/data/zeta3_digits.txt")

    # Database Paths
    catalan_sqlite_db: str = Field(default="/app/data/catalan_chunks.db")
    e_sqlite_db: str = Field(default="/app/data/e_chunks.db")
    eulers_sqlite_db: str = Field(default="/app/data/eulers_chunks.db")
    lemniscate_sqlite_db: str = Field(default="/app/data/lemniscate_chunks.db")
    log10_sqlite_db: str = Field(default="/app/data/log10_chunks.db")
    log2_sqlite_db: str = Field(default="/app/data/log2_chunks.db")
    log3_sqlite_db: str = Field(default="/app/data/log3_chunks.db")
    phi_sqlite_db: str = Field(default="/app/data/phi_chunks.db")
    pi_sqlite_db: str = Field(default="/app/data/pi_chunks.db")
    sqrt2_sqlite_db: str = Field(default="/app/data/sqrt2_chunks.db")
    sqrt3_sqlite_db: str = Field(default="/app/data/sqrt3_chunks.db")
    zeta3_sqlite_db: str = Field(default="/app/data/zeta3_chunks.db")

    # Binary Cache Paths
    catalan_binary_file: str = Field(default="/app/data/catalan_binary.dat")
    e_binary_file: str = Field(default="/app/data/e_binary.dat")
    eulers_binary_file: str = Field(default="/app/data/eulers_binary.dat")
    lemniscate_binary_file: str = Field(default="/app/data/lemniscate_binary.dat")
    log10_binary_file: str = Field(default="/app/data/log10_binary.dat")
    log2_binary_file: str = Field(default="/app/data/log2_binary.dat")
    log3_binary_file: str = Field(default="/app/data/log3_binary.dat")
    phi_binary_file: str = Field(default="/app/data/phi_binary.dat")
    pi_binary_file: str = Field(default="/app/data/pi_binary.dat")
    sqrt2_binary_file: str = Field(default="/app/data/sqrt2_binary.dat")
    sqrt3_binary_file: str = Field(default="/app/data/sqrt3_binary.dat")
    zeta3_binary_file: str = Field(default="/app/data/zeta3_binary.dat")

    # Storage Configuration
    chunk_size: int = Field(default=10000, description="Chunk size for storage")
    verify_every: int = Field(default=100, description="Verify every N requests")
    max_search_results: int = Field(default=1000, description="Max search results")
    default_digits_limit: int = Field(default=100000, description="Default digits limit")

    # Security & API Keys
    secret_key: str = Field(default="change-this-secret-key", description="Secret key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(default=None, description="Google API key")

    # Rate Limiting
    rate_limit_requests: int = Field(default=1000, description="Rate limit requests")
    rate_limit_window: int = Field(default=3600, description="Rate limit window")

    # Cache Settings
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    cache_ttl: int = Field(default=3600, description="Cache TTL")
    enable_cache: bool = Field(default=True, description="Enable cache")

    # Database Settings
    database_url: str = Field(
        default="sqlite:///./data/math_constants.db",
        description="Database URL"
    )
    database_pool_size: int = Field(default=10, description="Database pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow")

    # Monitoring & Metrics
    enable_metrics: bool = Field(default=True, description="Enable metrics")
    metrics_port: int = Field(default=9090, description="Metrics port")
    health_check_interval: int = Field(default=30, description="Health check interval")

    # Development Settings
    reload_on_change: bool = Field(default=True, description="Reload on change")
    reload_dirs: List[str] = Field(default=["/app"], description="Reload directories")
    hot_reload: bool = Field(default=True, description="Hot reload")

    # Testing
    test_data_size: int = Field(default=1000, description="Test data size")
    test_verification_samples: int = Field(
        default=100, description="Test verification samples"
    )


# Global settings instance
settings = Settings()