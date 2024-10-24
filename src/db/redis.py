from redis import asyncio as aioredis
from src.config import Config

#which is same with ACCESS_TOKEN_EXPIRY = 3600
#i only add access tokens to blocklist. 
#if i add any access token to blocklist i am sure that it will expired anyway becasue ACCESS_TOKEN_EXPIRY = JTI_EXPIRY
JTI_EXPIRY = 3600

""" token_blocklist = aioredis.StrictRedis(
    host = Config.REDIS_HOST,
    port = Config.REDIS_PORT,
    db=0
) """
token_blocklist = aioredis.from_url(
    f"redis://{Config.REDIS_HOST}:{Config.REDIS_PORT}",
    db=0,
    encoding="utf-8",
    decode_responses=True
)

async def add_jti_to_blocklist(jti : str) -> None:
    await token_blocklist.set(
        name=jti,
        value="",
        ex=JTI_EXPIRY
    )

async def token_in_blocklist(jti : str) -> bool:
    token_jti = await token_blocklist.get(jti)
    return token_jti is not None

# admin
[
    "adding users",
    "change roles",
    "crud on users",
    "book submissions",
    "crud on users",
    "crud on reviews",
    "revoking access",
]

#users
["crud on their own book submissions", "crud on their reviews", "crud on their own accounts"]