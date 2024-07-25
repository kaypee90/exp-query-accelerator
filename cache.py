"""
In-Memory key-value pair cache
"""

REQUEST_CACHE = {}

# TODO: Set TTL on cache with a naive implementation {"key": {"expiry":"yyyy-MM-dd", "value":"DATA"}}
class Cache:

    @staticmethod
    def set(request, result):
        REQUEST_CACHE[request] = result

    @staticmethod
    def get(request):
        return REQUEST_CACHE.get(request, None)
    
    @staticmethod
    def flush():
        REQUEST_CACHE.clear()
