"""Destructive integration tests run only in an explicitly named disposable database."""

import asyncio
import os
from collections.abc import Iterator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.fixture(scope="session")
def migrated_database() -> Iterator[str]:
    url = os.environ.get("AIFAMS_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set AIFAMS_TEST_DATABASE_URL to a disposable PostgreSQL database")
    parsed = make_url(url)
    if not (parsed.database or "").startswith("aifams_test"):
        pytest.fail(
            "Integration database name must start with aifams_test; refuses destructive tests"
        )
    if parsed.drivername != "postgresql+asyncpg":
        pytest.fail("Integration tests require PostgreSQL with asyncpg")
    old_url = os.environ.get("AIFAMS_MIGRATION_DATABASE_URL")
    os.environ["AIFAMS_MIGRATION_DATABASE_URL"] = url
    config = Config("alembic.ini")

    async def empty_database() -> None:
        engine = create_async_engine(url)
        try:
            async with engine.connect() as connection:
                count = await connection.scalar(
                    text("""
                    SELECT count(*) FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_name <> 'alembic_version'
                """)
                )
                assert count == 0, "Integration database is not empty; no data was deleted"
        finally:
            await engine.dispose()

    async def no_runtime_template_privileges() -> None:
        engine = create_async_engine(url)
        try:
            async with engine.connect() as connection:
                assert not await connection.scalar(
                    text("""
                    SELECT has_column_privilege('aifams_app', 'biometric_templates', 'id', 'SELECT')
                """)
                )
        finally:
            await engine.dispose()

    try:
        asyncio.run(empty_database())
        command.upgrade(config, "head")
        command.check(config)
        command.downgrade(config, "0001")
        asyncio.run(no_runtime_template_privileges())
        command.upgrade(config, "head")
        command.downgrade(config, "base")
        asyncio.run(empty_database())
        command.upgrade(config, "head")
        command.check(config)
        yield url
    finally:
        # Leave test data for investigation on failure; next run needs a new empty test DB.
        if old_url is None:
            os.environ.pop("AIFAMS_MIGRATION_DATABASE_URL", None)
        else:
            os.environ["AIFAMS_MIGRATION_DATABASE_URL"] = old_url
