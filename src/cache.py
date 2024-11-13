"""
In-Memory key-value pair cache
"""

from datetime import datetime, timedelta


TTL = 86400
CACHE_STORE = {}


class Cache:
    data_value_key = "value"

    @classmethod
    def set(cls, key, value, ttl=None):
        """
        Persists data to the cache store.

        Args:
            key (bytes or str): The key for the cache.
            value (int or float): The first number.
            ttl (int): The time to live in seconds. Defaults to 86400 (1 day).

        Returns:
            None
        """
        enriched_data = cls.__format_data(value, ttl)
        CACHE_STORE[key] = enriched_data

    @classmethod
    def get(cls, key):
        """
        Retrieves data from the cache store.

        Args:
            key (bytes or str): The key for the cache.

        Returns:
            list or dict: The data stored in the cache.
        """
        return cls.__get(key)

    @staticmethod
    def flush():
        """
        Clears the cache store.

        Returns:
            None
        """
        CACHE_STORE.clear()

    @classmethod
    def __get(cls, key):
        data = CACHE_STORE.get(key, None)
        if not data:
            return

        if data["expiry"] <= datetime.now():
            del CACHE_STORE[key]
            return

        return data.get(cls.data_value_key)

    @classmethod
    def __format_data(cls, value, ttl=None):
        if not ttl:
            ttl = TTL
        time_delta = timedelta(seconds=ttl)
        date_of_expiry = datetime.now() + time_delta
        return {"expiry": date_of_expiry, cls.data_value_key: value}
