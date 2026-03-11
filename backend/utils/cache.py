"""Redis cache utility helpers."""
from flask_caching import Cache

cache = Cache()


def init_cache(app):
    """Initialize the Flask-Caching extension with the app.
    Tries Redis first, falls back to SimpleCache if unavailable.
    """
    redis_url = app.config.get('CACHE_REDIS_URL', 'redis://localhost:6379/0')
    use_redis = False

    # Test Redis connectivity before configuring
    try:
        import redis
        r = redis.from_url(redis_url, socket_connect_timeout=2)
        r.ping()
        use_redis = True
        print("[✓] Redis connected — using RedisCache")
    except Exception:
        print("[!] Redis not available — using SimpleCache fallback")

    if use_redis:
        cache.init_app(app, config={
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': redis_url,
            'CACHE_DEFAULT_TIMEOUT': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
        })
    else:
        cache.init_app(app, config={
            'CACHE_TYPE': 'SimpleCache',
            'CACHE_DEFAULT_TIMEOUT': 300
        })


def safe_delete_memoized(func):
    """Safely delete memoized cache for a function."""
    try:
        cache.delete_memoized(func)
    except Exception:
        pass


def clear_cache_for(key_prefix):
    """Clear all cache entries with a given prefix."""
    try:
        cache.delete_memoized(key_prefix)
    except Exception:
        pass


def clear_all_cache():
    """Clear all cached data."""
    try:
        cache.clear()
    except Exception:
        pass
