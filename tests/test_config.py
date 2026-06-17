import os
from unittest.mock import patch


class TestConfig:
    def test_token_reads_env(self):
        with patch.dict(os.environ, {"TOKEN": "test-token-123", "ADMIN_ID": "0"}):
            import importlib
            import config
            importlib.reload(config)
            assert config.TOKEN == "test-token-123"

    def test_token_none_when_unset(self):
        env = os.environ.copy()
        env.pop("TOKEN", None)
        env.setdefault("ADMIN_ID", "0")
        with patch.dict(os.environ, env, clear=True):
            import importlib
            import config
            importlib.reload(config)
            assert config.TOKEN is None

    def test_admin_id_reads_env(self):
        with patch.dict(os.environ, {"TOKEN": "", "ADMIN_ID": "999"}):
            import importlib
            import config
            importlib.reload(config)
            assert config.ADMIN_ID == 999

    def test_admin_id_defaults_to_zero(self):
        env = os.environ.copy()
        env.pop("ADMIN_ID", None)
        env.setdefault("TOKEN", "")
        with patch.dict(os.environ, env, clear=True):
            import importlib
            import config
            importlib.reload(config)
            assert config.ADMIN_ID == 0
