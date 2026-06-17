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


TOKEN = _required_env("TOKEN")
ADMIN_ID = _required_int_env("ADMIN_ID")
