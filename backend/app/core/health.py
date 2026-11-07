import asyncio

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import Settings


async def check_dependencies(settings: Settings) -> dict[str, bool]:
    async def database() -> bool:
        engine = create_async_engine(settings.database_url)
        try:
            async with asyncio.timeout(3):
                async with engine.connect() as connection:
                    await connection.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
        finally:
            await engine.dispose()

    async def cache() -> bool:
        client: Redis = Redis.from_url(
            settings.redis_url, socket_connect_timeout=2, socket_timeout=2
        )
        try:
            async with asyncio.timeout(3):
                return bool(await client.ping())
        except Exception:
            return False
        finally:
            await client.aclose()

    db_ok, cache_ok = await asyncio.gather(database(), cache())
    return {"database": db_ok, "redis": cache_ok}
