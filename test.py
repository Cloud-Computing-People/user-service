import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.lpush('celery', '{"task": "test", "args": [], "kwargs": {}}')
print("Queue Length:", r.llen('celery'))