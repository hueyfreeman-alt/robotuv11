import os

def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _required_int_env(name: str) -> int:
    value = _required_env(name)
    try:
        parsed = int(value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be a number") from exc
    if parsed <= 0:
        raise RuntimeError(f"Environment variable {name} must be greater than 0")
    return parsed


def _optional_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _optional_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be a number") from exc


TOKEN = _required_env("TOKEN")
ADMIN_ID = _required_int_env("ADMIN_ID")

OXAPAY_MERCHANT_API_KEY = _required_env("OXAPAY_MERCHANT_API_KEY")
OXAPAY_CALLBACK_URL = _required_env("OXAPAY_CALLBACK_URL")
OXAPAY_RETURN_URL = os.getenv("OXAPAY_RETURN_URL", "")
OXAPAY_CURRENCY = os.getenv("OXAPAY_CURRENCY", "")
OXAPAY_SANDBOX = _optional_bool_env("OXAPAY_SANDBOX", False)

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = _optional_int_env("WEBHOOK_PORT", 8080)
