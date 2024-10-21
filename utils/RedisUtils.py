import redis
from retrying import retry

class RedisUtils:
    # Redis 连接属性，用户提供
    host = "152.32.175.149"
    port = 6379
    db = 0
    password = 'Mh359687..'
    # 私有构造函数
    _redis_client = None
    vip_91_article_links = 'vip_91_article_links'
    res_21zys_com_titles = "res_21zys_com_titles"
    @classmethod
    def _initialize_client(cls):
        if cls._redis_client is None:
            cls._redis_client = redis.StrictRedis(
                host=cls.host,
                port=cls.port,
                db=cls.db,
                password=cls.password,
                decode_responses=True
            )

    # ------------------ String 类型操作 ------------------
    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def set_string(cls, key: str, value: str):
        cls._initialize_client()
        return cls._redis_client.set(key, value)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_string(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.get(key)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def del_key(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.delete(key)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def update_string(cls, key: str, value: str):
        cls._initialize_client()
        return cls._redis_client.set(key, value)

    # ------------------ List 类型操作 ------------------
    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def push_list(cls, key: str, *values):
        cls._initialize_client()
        return cls._redis_client.rpush(key, *values)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_list(cls, key: str, start: int = 0, end: int = -1):
        cls._initialize_client()
        return cls._redis_client.lrange(key, start, end)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def pop_list(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.lpop(key)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def list_length(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.llen(key)

    # ------------------ Set 类型操作 ------------------
    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def add_set(cls, key: str, *values):
        cls._initialize_client()
        return cls._redis_client.sadd(key, *values)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_set(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.smembers(key)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def rem_set(cls, key: str, *values):
        cls._initialize_client()
        return cls._redis_client.srem(key, *values)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def set_length(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.scard(key)

    # ------------------ Hash 类型操作 ------------------
    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def set_hash(cls, key: str, field: str, value: str):
        cls._initialize_client()
        return cls._redis_client.hset(key, field, value)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_hash(cls, key: str, field: str):
        cls._initialize_client()
        return cls._redis_client.hget(key, field)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_all_hash(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.hgetall(key)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def del_hash(cls, key: str, field: str):
        cls._initialize_client()
        return cls._redis_client.hdel(key, field)

    # ------------------ Zset 类型操作 ------------------
    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def add_zset(cls, key: str, score: float, value: str):
        cls._initialize_client()
        return cls._redis_client.zadd(key, {value: score})

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def get_zset(cls, key: str, start: int = 0, end: int = -1, withscores: bool = False):
        cls._initialize_client()
        return cls._redis_client.zrange(key, start, end, withscores=withscores)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def rem_zset(cls, key: str, *values):
        cls._initialize_client()
        return cls._redis_client.zrem(key, *values)

    @classmethod
    @retry(stop_max_attempt_number=5, wait_fixed=2000)
    def zset_length(cls, key: str):
        cls._initialize_client()
        return cls._redis_client.zcard(key)

if __name__ == '__main__':
    RedisUtils.set_string('test', 'test')