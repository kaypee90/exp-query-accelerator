"""
In-memory key-value cache with per-entry TTL and LRU eviction.
"""

import time
from collections import OrderedDict

TTL = 86400
MAX_ENTRIES = 10_000
CACHE_STORE = OrderedDict()


class Cache:
    max_entries = MAX_ENTRIES

    @classmethod
    def set(cls, key, value, ttl=None):
        """
        Persists data to the cache store, evicting the least recently used
        entry when the store is full.

        Args:
            key (bytes or str): The key for the cache.
            value (Any): The value to cache.
            ttl (int | float | None): Time to live in seconds. Defaults to TTL (1 day).

        Returns:
            None
        """
        if ttl is None:
            ttl = TTL
        CACHE_STORE[key] = (time.monotonic() + ttl, value)
        CACHE_STORE.move_to_end(key)
        while len(CACHE_STORE) > cls.max_entries:
            CACHE_STORE.popitem(last=False)

    @staticmethod
    def get(key):
        """
        Retrieves data from the cache store.

        Args:
            key (bytes or str): The key for the cache.

        Returns:
            The cached value, or None if the key is missing or expired.
        """
        entry = CACHE_STORE.get(key)
        if entry is None:
            return None

        expiry, value = entry
        if expiry <= time.monotonic():
            del CACHE_STORE[key]
            return None

        CACHE_STORE.move_to_end(key)
        return value

    @staticmethod
    def flush():
        """
        Clears the cache store.

        Returns:
            None
        """
        CACHE_STORE.clear()
