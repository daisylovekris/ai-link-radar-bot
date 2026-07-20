import os
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

os.environ.setdefault("BOT_TOKEN", "1234567890:AAFakeTokenForTestingPurposesOnly")
os.environ.setdefault("OPENAI_API_KEY", "sk-fake-test-key-do-not-use")

_fake_openai_module = MagicMock()
sys.modules.setdefault("openai", _fake_openai_module)
