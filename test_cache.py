from cache import Cache


def test_cache_get_with_valid_key():
    data = '{"table":"products"}'
    Cache.set("valid_key", data)

    assert Cache.get("valid_key") == data


def test_cache_get_with_expired_key():
    data = '{"table":"expired"}'
    Cache.set("expired_key", data, -1)

    assert Cache.get("expired_key") == None


def test_cache_get_with_non_existing_key():
    value = Cache.get("non_existing_key")
    assert value == None


def test_cache_flush():
    data = '{"data": ["test", "items"]}'
    Cache.set("sample_key", data)

    Cache.flush()

    assert Cache.get("sample_key") == None
