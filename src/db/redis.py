import aioredis
from src.config import Config

#which is same with ACCESS_TOKEN_EXPIRY = 3600
#i only add access tokens to blocklist. 
#if i add any access token to blocklist i am sure that it will expired anyway becasue ACCESS_TOKEN_EXPIRY = JTI_EXPIRY
JTI_EXPIRY = 3600

token_blocklist = aioredis.StrictRedis(
    host = Config.REDIS_HOST,
    port = Config.REDIS_PORT,
    db=0
)

async def add_jti_to_blocklist(jti : str) -> None:
    await token_blocklist.set(
        name=jti,
        value="",
        exp=JTI_EXPIRY
    )

async def token_in_blocklist(jti : str) -> bool:
    token_jti = await token_blocklist.get(jti)
    return token_jti is not None
