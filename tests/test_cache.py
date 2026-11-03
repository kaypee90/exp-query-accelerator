import pytest

from src.cache import Cache


class TestCache:
    def test_cache_get_with_valid_key(self):
        data = '{"table":"products"}'
        Cache.set("valid_key", data)

        assert Cache.get("valid_key") == data

    def test_cache_get_with_expired_key(self):
        data = '{"table":"expired"}'
        Cache.set("expired_key", data, -1)

        assert Cache.get("expired_key") is None

    def test_cache_zero_ttl_expires_immediately(self):
        Cache.set("zero_ttl", "value", 0)

        assert Cache.get("zero_ttl") is None

    def test_cache_get_with_non_existing_key(self):
        assert Cache.get("non_existing_key") is None

    @pytest.mark.parametrize("value", [[], 0, "", False])
    def test_cache_stores_falsy_values(self, value):
        Cache.set("falsy", value)

        assert Cache.get("falsy") == value

    def test_cache_set_overwrites_existing_key(self):
        Cache.set("key", "old")
        Cache.set("key", "new")

        assert Cache.get("key") == "new"

    def test_cache_flush(self):
        data = '{"data": ["test", "items"]}'
        Cache.set("sample_key", data)

        Cache.flush()

        assert Cache.get("sample_key") is None

    def test_cache_evicts_least_recently_used(self, monkeypatch):
        monkeypatch.setattr(Cache, "max_entries", 2)
        Cache.set("a", 1)
        Cache.set("b", 2)
        Cache.get("a")  # "a" is now more recently used than "b"
        Cache.set("c", 3)

        assert Cache.get("b") is None
        assert Cache.get("a") == 1
        assert Cache.get("c") == 3
