from cache import Cache


class TestCache:
    def test_cache_get_with_valid_key(self):
        data = '{"table":"products"}'
        Cache.set("valid_key", data)

        assert Cache.get("valid_key") == data

    def test_cache_get_with_expired_key(self):
        data = '{"table":"expired"}'
        Cache.set("expired_key", data, -1)

        assert Cache.get("expired_key") is None

    def test_cache_get_with_non_existing_key(self):
        value = Cache.get("non_existing_key")
        assert value is None

    def test_cache_flush(self):
        data = '{"data": ["test", "items"]}'
        Cache.set("sample_key", data)

        Cache.flush()

        assert Cache.get("sample_key") is None
