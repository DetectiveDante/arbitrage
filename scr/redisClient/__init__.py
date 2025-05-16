import redis.asyncio as redis


connectionPool = redis.ConnectionPool(host='redis', port=6379, db=0, max_connections=10)

def get_connection():
    return redis.Redis(connection_pool=connectionPool)