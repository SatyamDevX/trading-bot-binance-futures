import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional during lightweight test runs
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


def get_binance_settings():
    return {
        "api_key": os.getenv("BINANCE_API_KEY", ""),
        "api_secret": os.getenv("BINANCE_API_SECRET", ""),
        "base_url": os.getenv("BINANCE_BASE_URL", ""),
    }


def validate_binance_settings():
    settings = get_binance_settings()
    missing = [
        env_name
        for env_name, value in (
            ("BINANCE_API_KEY", settings["api_key"]),
            ("BINANCE_API_SECRET", settings["api_secret"]),
            ("BINANCE_BASE_URL", settings["base_url"]),
        )
        if not value
    ]
    if missing:
        raise ValueError(
            "Missing required environment variables: " + ", ".join(missing)
        )
    return settings


def get_public_config_status():
    settings = get_binance_settings()
    return {
        "has_api_key": bool(settings["api_key"]),
        "has_api_secret": bool(settings["api_secret"]),
        "has_base_url": bool(settings["base_url"]),
        "base_url": settings["base_url"] or "Not configured",
    }
