from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


@asynccontextmanager
async def tenant_transaction(
    engine: AsyncEngine, institution_id: UUID
) -> AsyncIterator[AsyncSession]:
    """Services own transactions. Call only with a tenant authorized by the policy layer.

    Transaction-local settings are cleared on commit/rollback, including pooled reuse.
    This is a DB boundary, not authentication or an authorization decision.
    """
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory.begin() as session:
        await session.execute(
            text("SELECT set_config('aifams.institution_id', :tenant, true)"),
            {"tenant": str(institution_id)},
        )
        yield session
