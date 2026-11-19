from fastapi import HTTPException, Request
from redis_client import redis_client


LOGIN_LIMIT_SCRIPT = """
local attempts = redis.call('INCR', KEYS[1])

if attempts == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end

return {attempts, redis.call('TTL', KEYS[1])}
"""


def limit_login_requests(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:login:{client_ip}"

    attempts, ttl = redis_client.eval(
        LOGIN_LIMIT_SCRIPT,
        1,
        key,
        60,
    )

    if attempts > 5:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Try again later.",
            headers={"Retry-After": str(max(ttl, 1))},
        )