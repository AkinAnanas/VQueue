import redis


redis_server = redis.Redis(host='localhost', port=6379, db=0)


def enqueue_party(block_id, party_id):
    key = f"queue:{block_id}"
    redis_server.rpush(key, party_id)

def dequeue_party(block_id):
    key = f"queue:{block_id}"
    return redis_server.lpop(key)

def get_queue(block_id):
    key = f"queue:{block_id}"
    return redis_server.lrange(key, 0, -1)

def remove_party(block_id, party_id):
    key = f"queue:{block_id}"
    redis_server.lrem(key, 0, party_id)

def get_queue_length(block_id):
    key = f"queue:{block_id}"
    return redis_server.llen(key)