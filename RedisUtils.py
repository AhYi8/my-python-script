import redis

class RedisUtils:
    # Redis 连接属性，用户提供
    host = "152.32.175.149"
    port = 6379
    db = 0
    password = None

    # 饿汉式初始化 Redis 客户端，确保客户端只初始化一次
    _redis_client = redis.StrictRedis(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=True
    )

    # ------------------ String 类型操作 ------------------
    @staticmethod
    def set_string(key: str, value: str):
        return RedisUtils._redis_client.set(key, value)

    @staticmethod
    def get_string(key: str):
        return RedisUtils._redis_client.get(key)

    @staticmethod
    def del_key(key: str):
        return RedisUtils._redis_client.delete(key)

    @staticmethod
    def update_string(key: str, value: str):
        return RedisUtils._redis_client.set(key, value)

    # ------------------ List 类型操作 ------------------
    @staticmethod
    def push_list(key: str, *values):
        return RedisUtils._redis_client.rpush(key, *values)

    @staticmethod
    def get_list(key: str, start: int = 0, end: int = -1):
        return RedisUtils._redis_client.lrange(key, start, end)

    @staticmethod
    def pop_list(key: str):
        return RedisUtils._redis_client.lpop(key)

    @staticmethod
    def list_length(key: str):
        return RedisUtils._redis_client.llen(key)

    # ------------------ Set 类型操作 ------------------
    @staticmethod
    def add_set(key: str, *values):
        return RedisUtils._redis_client.sadd(key, *values)

    @staticmethod
    def get_set(key: str):
        return RedisUtils._redis_client.smembers(key)

    @staticmethod
    def rem_set(key: str, *values):
        return RedisUtils._redis_client.srem(key, *values)

    @staticmethod
    def set_length(key: str):
        return RedisUtils._redis_client.scard(key)

    # ------------------ Hash 类型操作 ------------------
    @staticmethod
    def set_hash(key: str, field: str, value: str):
        return RedisUtils._redis_client.hset(key, field, value)

    @staticmethod
    def get_hash(key: str, field: str):
        return RedisUtils._redis_client.hget(key, field)

    @staticmethod
    def get_all_hash(key: str):
        return RedisUtils._redis_client.hgetall(key)

    @staticmethod
    def del_hash(key: str, field: str):
        return RedisUtils._redis_client.hdel(key, field)

    # ------------------ Zset 类型操作 ------------------
    @staticmethod
    def add_zset(key: str, score: float, value: str):
        return RedisUtils._redis_client.zadd(key, {value: score})

    @staticmethod
    def get_zset(key: str, start: int = 0, end: int = -1, withscores: bool = False):
        return RedisUtils._redis_client.zrange(key, start, end, withscores=withscores)

    @staticmethod
    def rem_zset(key: str, *values):
        return RedisUtils._redis_client.zrem(key, *values)

    @staticmethod
    def zset_length(key: str):
        return RedisUtils._redis_client.zcard(key)


if __name__ == '__main__':
    RedisUtils.set_string('test', 'test')