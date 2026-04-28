"""
CORS Security Configuration.
"""

import os
from dataclasses import dataclass


@dataclass
class CORSConfig:
    """
    CORS configuration settings.
    """

    allowed_origins: list[str]
    allowed_methods: list[str]
    allowed_headers: list[str]
    exposed_headers: list[str]
    allow_credentials: bool = True
    max_age: int = 86400  # 24 hours


def load_cors_config() -> CORSConfig:
    """
    Load CORS configuration from environment.
    """
    origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080")

    return CORSConfig(
        allowed_origins=origins_str.split(","),
        allowed_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allowed_headers=[
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-CSRF-Token",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
        ],
        exposed_headers=["X-Total-Count", "X-Page-Count"],
        allow_credentials=os.getenv("ALLOW_CREDENTIALS", "true").lower() == "true",
        max_age=int(os.getenv("CORS_MAX_AGE", "86400")),
    )


def get_cors_headers(origin: str, method: str = "GET") -> dict[str, str]:
    """
    Generate CORS headers for a given request.
    """
    config = load_cors_config()

    headers = {}

    if origin in config.allowed_origins or "*" in config.allowed_origins:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Methods"] = ", ".join(config.allowed_methods)
        headers["Access-Control-Allow-Headers"] = ", ".join(config.allowed_headers)

        if config.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"

        headers["Access-Control-Max-Age"] = str(config.max_age)

        if config.exposed_headers:
            headers["Access-Control-Expose-Headers"] = ", ".join(config.exposed_headers)

    return headers


# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    ),
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": (
        "geolocation=(), microphone=(), camera=(), payment=(), usb=()"
    ),
}


def add_security_headers(headers: dict[str, str]) -> dict[str, str]:
    """
    Add security headers to response.
    """
    headers.update(SECURITY_HEADERS)
    return headers
