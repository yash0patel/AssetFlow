"""
app/core/constants.py
──────────────────────
Application-wide constants and enumerations.
Pure data — no imports from the rest of the app.
"""

# ── API versioning ─────────────────────────────────────────────────────────────
API_V1_PREFIX = "/api/v1"

# ── Pagination defaults ────────────────────────────────────────────────────────
DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ── Cache TTLs (seconds) ───────────────────────────────────────────────────────
CACHE_TTL_SHORT = 60           # 1 minute
CACHE_TTL_MEDIUM = 300         # 5 minutes
CACHE_TTL_LONG = 1800          # 30 minutes
CACHE_TTL_DAY = 86400          # 24 hours

# ── Redis key prefixes ─────────────────────────────────────────────────────────
REDIS_PREFIX_SESSION = "session:"
REDIS_PREFIX_RATE_LIMIT = "rate_limit:"
REDIS_PREFIX_CACHE = "cache:"
REDIS_PREFIX_OTP = "otp:"

# ── Rate limiting ──────────────────────────────────────────────────────────────
RATE_LIMIT_REQUESTS = 100      # requests per window
RATE_LIMIT_WINDOW = 60         # window in seconds

# ── Upload ─────────────────────────────────────────────────────────────────────
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_DOC_TYPES = {"application/pdf"}
