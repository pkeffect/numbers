"""
Mathematical Constants Configuration

Defines all supported mathematical constants with their properties and known prefixes.
"""

from typing import Dict, NamedTuple


class MathConstant(NamedTuple):
    """Mathematical constant definition"""
    name: str
    symbol: str
    description: str
    known_prefix: str  # First 50 digits for verification
    filename: str


# All supported mathematical constants
MATH_CONSTANTS: Dict[str, MathConstant] = {
    "catalan": MathConstant(
        name="Catalan",
        symbol="G",
        description="Catalan constant",
        known_prefix="91596559417721901505460351493238411077414937428167",
        filename="catalan_digits.txt"
    ),
    "e": MathConstant(
        name="Euler's number",
        symbol="e",
        description="Base of natural logarithm",
        known_prefix="27182818284590452353602874713526624977572470936999",
        filename="e_digits.txt"
    ),
    "eulers": MathConstant(
        name="Euler-Mascheroni",
        symbol="γ",
        description="Euler-Mascheroni constant",
        known_prefix="57721566490153286060651209008240243104215933593992",
        filename="eulers_digits.txt"
    ),
    "lemniscate": MathConstant(
        name="Lemniscate",
        symbol="ϖ",
        description="Lemniscate constant",
        known_prefix="26205830904531276522748574649951968533133071993113",
        filename="lemniscate_digits.txt"
    ),
    "log10": MathConstant(
        name="Natural log of 10",
        symbol="ln(10)",
        description="Natural logarithm of 10",
        known_prefix="23025850929940456840179914546843642076011014886287",
        filename="log10_digits.txt"
    ),
    "log2": MathConstant(
        name="Natural log of 2",
        symbol="ln(2)",
        description="Natural logarithm of 2",
        known_prefix="69314718055994530941723212145817656807550013436025",
        filename="log2_digits.txt"
    ),
    "log3": MathConstant(
        name="Natural log of 3",
        symbol="ln(3)",
        description="Natural logarithm of 3",
        known_prefix="10986122886681096913952452369225257046474905578227",
        filename="log3_digits.txt"
    ),
    "phi": MathConstant(
        name="Golden Ratio",
        symbol="φ",
        description="(1 + √5) / 2",
        known_prefix="16180339887498948482045868343656381177203091798057",
        filename="phi_digits.txt"
    ),
    "pi": MathConstant(
        name="Pi",
        symbol="π",
        description="Ratio of circumference to diameter",
        known_prefix="31415926535897932384626433832795028841971693993751",
        filename="pi_digits.txt"
    ),
    "sqrt2": MathConstant(
        name="Square Root of 2",
        symbol="√2",
        description="√2",
        known_prefix="14142135623730950488016887242096980785696718753769",
        filename="sqrt2_digits.txt"
    ),
    "sqrt3": MathConstant(
        name="Square Root of 3",
        symbol="√3", 
        description="√3",
        known_prefix="17320508075688772935274463415058723669428052538103",
        filename="sqrt3_digits.txt"
    ),
    "zeta3": MathConstant(
        name="Apéry's constant",
        symbol="ζ(3)",
        description="Riemann zeta function ζ(3)",
        known_prefix="12020569031595942853997381615114499907649862923404",
        filename="zeta3_digits.txt"
    ),
}

# Quick access to known prefixes for verification
KNOWN_PREFIXES: Dict[str, str] = {
    constant_id: constant.known_prefix 
    for constant_id, constant in MATH_CONSTANTS.items()
}

# File mapping for configuration
CONSTANT_FILES: Dict[str, str] = {
    constant_id: constant.filename
    for constant_id, constant in MATH_CONSTANTS.items()
}

# Display names for API responses
CONSTANT_DISPLAY_NAMES: Dict[str, str] = {
    constant_id: f"{constant.name} ({constant.symbol})"
    for constant_id, constant in MATH_CONSTANTS.items()
}

# Verification constants (first 10 digits for quick health checks)
HEALTH_CHECK_PREFIXES: Dict[str, str] = {
    "catalan": "9159655941",
    "e": "2718281828",
    "eulers": "5772156649", 
    "lemniscate": "2620583090",
    "log10": "2302585092",
    "log2": "6931471805",
    "log3": "1098612288",
    "phi": "1618033988",
    "pi": "3141592653",
    "sqrt2": "1414213562",
    "sqrt3": "1732050807",
    "zeta3": "1202056903",
}