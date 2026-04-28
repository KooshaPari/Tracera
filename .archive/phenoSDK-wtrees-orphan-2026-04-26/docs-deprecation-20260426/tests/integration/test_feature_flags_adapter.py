import asyncio
import sys
from pathlib import Path

# Import adapters as a top-level package by inserting adapter-kit on sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "adapter-kit"))
from adapters.feature_flags import FeatureFlagAdapter  # type: ignore  # noqa: E402


class DummyFFAdapter(FeatureFlagAdapter):
    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    async def health_check(self) -> bool:
        return True

    async def is_enabled(self, key: str, default: bool = False) -> bool:
        # simple behavior: enabled if context has flag "enable_all"
        return bool(self._context.get("enable_all", default))

    async def get_variant(self, key: str, default=None):
        return self._context.get(key, default)


def test_feature_flag_adapter_basic():
    adapter = DummyFFAdapter()
    adapter.connect()
    assert adapter.is_connected()

    adapter.set_context({"user_id": "u1", "plan": "pro"})

    loop = asyncio.get_event_loop()
    assert loop.run_until_complete(adapter.is_enabled("flag", default=False)) is False
    assert loop.run_until_complete(adapter.get_variant("plan", default="free")) == "pro"

    loop.run_until_complete(adapter.track_event("clicked", {"a": 1}))  # should not raise

    adapter.disconnect()
    assert not adapter.is_connected()
