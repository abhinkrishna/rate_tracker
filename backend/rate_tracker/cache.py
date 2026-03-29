from django.core.cache import cache as default_cache

class CacheUtility:
    """
    Utility class for interacting with the Redis cache.
    """
    def __init__(self, cache_backend=None):
        self.cache = cache_backend or default_cache

    def get(self, key, default=None):
        return self.cache.get(key, default)

    def set(self, key, value, timeout=None):
        if timeout is not None:
            return self.cache.set(key, value, timeout=timeout)
        return self.cache.set(key, value)

    def delete(self, key):
        return self.cache.delete(key)

    def delete_pattern(self, pattern):
        if hasattr(self.cache, 'delete_pattern'):
            return self.cache.delete_pattern(pattern)
        elif hasattr(self.cache, 'clear'):
            self.cache.clear()
        return None
