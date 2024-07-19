"""
In-Memory key-value pair cache
"""
# TODO: Improve to be a specialized class based in-memory cache
REQUEST_CACHE = {}

def cache_request(request, result):
    REQUEST_CACHE[request] = result

def get_cached_request(request):
    return REQUEST_CACHE.get(request, None)