# app/api/routers/__init__.py
"""
API Routers Package

Dedicated routers for each mathematical constant plus general and admin endpoints.

Structure:
    - general: Root, health, list constants
    - admin: Bulk operations and system maintenance
    - legacy: Backward-compatible parameterized endpoints (deprecated)
    - Individual constant routers: pi, e, phi, sqrt2, sqrt3, catalan, eulers, 
                                   lemniscate, log2, log3, log10, zeta3

Each constant router provides 7 endpoints:
    - GET /{constant}/status      - Status and cache information
    - GET /{constant}/digits       - Retrieve digits from position
    - GET /{constant}/search       - Search for digit sequences
    - GET /{constant}/stats        - Statistical analysis
    - GET /{constant}/random       - Get random digits
    - POST /{constant}/build-cache - Build SQLite and binary cache
    - POST /{constant}/verify      - Verify data integrity
"""

from app.api.routers import (
    general,
    admin,
    legacy,
    pi,
    e,
    phi,
    sqrt2,
    sqrt3,
    catalan,
    eulers,
    lemniscate,
    log2,
    log3,
    log10,
    zeta3
)

__all__ = [
    "general",
    "admin",
    "legacy",
    "pi",
    "e",
    "phi",
    "sqrt2",
    "sqrt3",
    "catalan",
    "eulers",
    "lemniscate",
    "log2",
    "log3",
    "log10",
    "zeta3"
]

# Router metadata for documentation
ROUTER_INFO = {
    "general": "Root, health check, and list constants",
    "admin": "Administrative bulk operations",
    "legacy": "Backward-compatible parameterized endpoints (deprecated)",
    "pi": "Pi (π) - Ratio of circumference to diameter",
    "e": "Euler's Number (e) - Base of natural logarithm",
    "phi": "Golden Ratio (φ) - (1 + √5) / 2",
    "sqrt2": "Square Root of 2 (√2)",
    "sqrt3": "Square Root of 3 (√3)",
    "catalan": "Catalan Constant (G)",
    "eulers": "Euler-Mascheroni Constant (γ)",
    "lemniscate": "Lemniscate Constant (ϖ)",
    "log2": "Natural Log of 2 (ln(2))",
    "log3": "Natural Log of 3 (ln(3))",
    "log10": "Natural Log of 10 (ln(10))",
    "zeta3": "Apéry's Constant (ζ(3))"
}

def get_router_description(router_name: str) -> str:
    """Get description for a router by name"""
    return ROUTER_INFO.get(router_name, "Unknown router")

def get_all_router_names() -> list:
    """Get list of all router names"""
    return list(__all__)

def get_constant_routers() -> list:
    """Get list of constant router names only (excludes general, admin, legacy)"""
    return [name for name in __all__ if name not in ["general", "admin", "legacy"]]