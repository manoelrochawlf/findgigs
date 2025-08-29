import redis

def get_redis_connection():
    client = redis.Redis(
        host="147.93.32.9",
        port=6379,
        username="default",
        password="b2aa64875274133840e4",
        decode_responses=True
    )
    return client
