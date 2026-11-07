import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import insert, select, text
from sqlalchemy.exc import DBAPIError, InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from app.core.database import tenant_transaction
from app.models import BiometricTemplate, metadata


@dataclass
class SampleTenant:
    institution: UUID
    user: UUID
    department: UUID
    year: UUID
    session: UUID


@asynccontextmanager
async def connection(url: str) -> AsyncIterator[AsyncConnection]:
    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            yield conn
    finally:
        await engine.dispose()


async def seed(conn: AsyncConnection) -> SampleTenant:
    data = SampleTenant(*(uuid4() for _ in range(5)))
    rows = {
        "institutions": {
            "id": data.institution,
            "code": str(data.institution),
            "name": "Test institution",
            "timezone": "Asia/Kolkata",
        },
        "users": {
            "id": data.user,
            "institution_id": data.institution,
            "email": f"{data.user}@example.invalid",
            "display_name": "Test user",
        },
        "departments": {
            "id": data.department,
            "institution_id": data.institution,
            "code": "TEST",
            "name": "Test department",
        },
        "academic_years": {
            "id": data.year,
            "institution_id": data.institution,
            "name": "Test year",
            "starts_on": datetime(2026, 1, 1).date(),
            "ends_on": datetime(2026, 12, 31).date(),
        },
        "attendance_sessions": {
            "id": data.session,
            "institution_id": data.institution,
            "academic_year_id": data.year,
            "department_id": data.department,
            "attendance_type": "class",
            "session_date": datetime.now(UTC).date(),
            "starts_at": datetime(2026, 1, 1, tzinfo=UTC),
            "ends_at": datetime(2026, 1, 2, tzinfo=UTC),
            "status": "open",
            "mode": "manual",
            "policy_snapshot": {},
        },
    }
    for table, values in rows.items():
        await conn.execute(insert(metadata.tables[table]).values(**values))
    return data


async def as_role(conn: AsyncConnection, tenant: UUID | None, *, biometric: bool = False) -> None:
    role = "aifams_biometric" if biometric else "aifams_app"
    await conn.execute(text(f"SET LOCAL ROLE {role}"))
    if tenant:
        await conn.execute(
            text("SELECT set_config('aifams.institution_id', :id, true)"), {"id": str(tenant)}
        )


async def seed_template(conn: AsyncConnection, tenant: SampleTenant) -> tuple[UUID, UUID, UUID]:
    notice, consent, model, template = (uuid4() for _ in range(4))
    rows = {
        "consent_notices": {
            "id": notice,
            "version": "v1",
            "purpose": "test",
            "language": "en",
            "text": "Test notice",
            "retention_days": 30,
        },
        "biometric_consents": {
            "id": consent,
            "user_id": tenant.user,
            "notice_id": notice,
            "granted_at": datetime.now(UTC),
            "ip_address": "127.0.0.1",
            "device_reference": "test",
            "language": "en",
        },
        "model_versions": {
            "id": model,
            "name": "Test fixture only",
            "version": "1",
            "checksum_sha256": "0" * 64,
            "license": "Test fixture",
            "artifact_reference": "fixture",
            "evaluation_metrics": {},
            "rollout_status": "candidate",
        },
        "biometric_templates": {
            "id": template,
            "user_id": tenant.user,
            "consent_id": consent,
            "model_version_id": model,
            "template_version": 1,
            "quality_score": 0.9,
            "expires_at": datetime(2099, 1, 1, tzinfo=UTC),
            "key_version": "fixture",
            "ciphertext": b"x" * 32,
            "wrapped_key": b"wrapped-fixture-key",
            "nonce": b"n" * 12,
        },
    }
    for table, values in rows.items():
        await conn.execute(
            insert(metadata.tables[table]).values(institution_id=tenant.institution, **values)
        )
    return template, model, consent


async def test_real_schema_and_forced_rls(migrated_database: str) -> None:
    async with connection(migrated_database) as conn:
        flags = (
            await conn.execute(
                text("""
            SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public' AND c.relkind = 'r' AND relname <> 'alembic_version'
        """)
            )
        ).all()
        assert len(flags) == len(metadata.tables)
        for name, enabled, forced in flags:
            assert (enabled, forced) == ((False, False) if name == "permissions" else (True, True))


async def test_missing_tenant_and_cross_tenant_access_fail_closed(migrated_database: str) -> None:
    async with connection(migrated_database) as conn:
        first, second = await seed(conn), await seed(conn)
    async with connection(migrated_database) as conn:
        await as_role(conn, None)
        assert await conn.scalar(text("SELECT count(*) FROM users")) == 0
        assert await conn.scalar(text("SELECT count(*) FROM institutions")) == 0
        await conn.execute(
            text("SELECT set_config('aifams.institution_id', :id, true)"),
            {"id": str(first.institution)},
        )
        assert (await conn.execute(text("SELECT id FROM users"))).scalars().all() == [first.user]
        assert (
            await conn.scalar(
                text("SELECT count(*) FROM users WHERE id = :id"), {"id": second.user}
            )
            == 0
        )
        updated = await conn.execute(
            text("UPDATE users SET display_name = 'blocked' WHERE id = :id"), {"id": second.user}
        )
        assert updated.rowcount == 0
    async with connection(migrated_database) as conn:
        await as_role(conn, first.institution)
        with pytest.raises(DBAPIError) as error:
            await conn.execute(
                insert(metadata.tables["departments"]).values(
                    institution_id=second.institution, code="BLOCKED", name="Blocked"
                )
            )
        assert error.value.orig.sqlstate == "42501"


async def test_cross_tenant_foreign_keys_reject_even_for_owner(migrated_database: str) -> None:
    async with connection(migrated_database) as conn:
        first, second = await seed(conn), await seed(conn)
    async with connection(migrated_database) as conn:
        with pytest.raises(DBAPIError) as error:
            await conn.execute(
                insert(metadata.tables["courses"]).values(
                    institution_id=first.institution,
                    department_id=second.department,
                    code="BAD",
                    name="Cross tenant",
                )
            )
        assert error.value.orig.sqlstate == "23503"


async def test_transaction_tenant_context_does_not_leak_through_pool(
    migrated_database: str,
) -> None:
    engine = create_async_engine(migrated_database, pool_size=1, max_overflow=0)
    try:
        async with engine.begin() as conn:
            first, second = await seed(conn), await seed(conn)
        for tenant in (first, second):
            async with tenant_transaction(engine, tenant.institution) as session:
                await session.execute(text("SET LOCAL ROLE aifams_app"))
                assert (await session.execute(text("SELECT id FROM users"))).scalars().all() == [
                    tenant.user
                ]
        with pytest.raises(RuntimeError, match="test rollback"):
            async with tenant_transaction(engine, first.institution) as session:
                await session.execute(text("SET LOCAL ROLE aifams_app"))
                raise RuntimeError("test rollback")
        async with engine.begin() as conn:
            await as_role(conn, None)
            assert await conn.scalar(text("SELECT count(*) FROM users")) == 0
    finally:
        await engine.dispose()


async def test_ciphertext_permissions_and_deferred_mapping(migrated_database: str) -> None:
    async with connection(migrated_database) as conn:
        tenant = await seed(conn)
        template, _, _ = await seed_template(conn, tenant)
    engine = create_async_engine(migrated_database)
    try:
        async with tenant_transaction(engine, tenant.institution) as session:
            await session.execute(text("SET LOCAL ROLE aifams_app"))
            instance = (
                await session.execute(
                    select(BiometricTemplate).where(
                        metadata.tables["biometric_templates"].c.id == template
                    )
                )
            ).scalar_one()
            with pytest.raises(InvalidRequestError):
                _ = instance.ciphertext
        async with engine.begin() as conn:
            await as_role(conn, tenant.institution)
            with pytest.raises(DBAPIError) as error:
                await conn.execute(text("SELECT ciphertext FROM biometric_templates"))
            assert error.value.orig.sqlstate == "42501"
        async with engine.begin() as conn:
            await as_role(conn, tenant.institution, biometric=True)
            assert (
                await conn.scalar(text("SELECT octet_length(ciphertext) FROM biometric_templates"))
                == 32
            )
    finally:
        await engine.dispose()


async def test_only_one_active_template_per_model_and_user(migrated_database: str) -> None:
    async with connection(migrated_database) as conn:
        tenant = await seed(conn)
        template, _, _ = await seed_template(conn, tenant)
    async with connection(migrated_database) as conn:
        with pytest.raises(DBAPIError) as error:
            await conn.execute(
                text("""
                INSERT INTO biometric_templates
                    (institution_id, user_id, consent_id, model_version_id, template_version,
                     quality_score, expires_at, is_active, key_version,
                     ciphertext, wrapped_key, nonce)
                SELECT institution_id, user_id, consent_id, model_version_id, 2, quality_score,
                       expires_at, true, key_version, ciphertext, wrapped_key, nonce
                FROM biometric_templates WHERE id = :id
            """),
                {"id": template},
            )
        assert error.value.orig.sqlstate == "23505"


@pytest.mark.parametrize(
    ("source", "status", "reason", "attempt", "outcome", "expected"),
    [
        ("face", "present", None, False, None, "23514"),
        ("face", "present", None, True, None, "23514"),
        ("face", "present", None, True, "rejected", "23514"),
        ("face", "present", None, True, "verified", "23503"),
        ("manual", "present", None, False, None, "23514"),
        ("manual", "present", "   ", False, None, "23514"),
        ("policy", "present", None, False, None, "23514"),
    ],
)
async def test_failed_verification_and_invalid_manual_marks_never_become_present(
    migrated_database: str,
    source: str,
    status: str,
    reason: str | None,
    attempt: bool,
    outcome: str | None,
    expected: str,
) -> None:
    async with connection(migrated_database) as conn:
        tenant = await seed(conn)
        _, model, _ = await seed_template(conn, tenant)
        attempt_id = uuid4()
        await conn.execute(
            insert(metadata.tables["verification_attempts"]).values(
                id=attempt_id,
                institution_id=tenant.institution,
                user_id=tenant.user,
                session_id=tenant.session,
                model_version_id=model,
                outcome="rejected",
                reason_codes=["test_rejection"],
                threshold_snapshot={},
                challenge_passed=False,
            )
        )
    async with connection(migrated_database) as conn:
        await as_role(conn, tenant.institution)
        with pytest.raises(DBAPIError) as error:
            await conn.execute(
                insert(metadata.tables["attendance_records"]).values(
                    institution_id=tenant.institution,
                    user_id=tenant.user,
                    session_id=tenant.session,
                    status=status,
                    source=source,
                    marked_by_user_id=tenant.user,
                    manual_reason=reason,
                    verification_attempt_id=attempt_id if attempt else None,
                    verification_outcome=outcome,
                )
            )
        assert error.value.orig.sqlstate == expected
    async with connection(migrated_database) as conn:
        assert (
            await conn.scalar(
                text("SELECT count(*) FROM attendance_records WHERE session_id = :id"),
                {"id": tenant.session},
            )
            == 0
        )


async def test_manual_attendance_uses_immutable_server_timestamp(migrated_database: str) -> None:
    async with connection(migrated_database) as conn:
        tenant = await seed(conn)
    async with connection(migrated_database) as conn:
        await as_role(conn, tenant.institution)
        recorded = (
            await conn.execute(
                insert(metadata.tables["attendance_records"])
                .values(
                    institution_id=tenant.institution,
                    user_id=tenant.user,
                    session_id=tenant.session,
                    status="manual",
                    source="manual",
                    marked_by_user_id=tenant.user,
                    manual_reason="Documented alternative",
                    marked_at=datetime(2000, 1, 1, tzinfo=UTC),
                )
                .returning(metadata.tables["attendance_records"].c.marked_at)
            )
        ).scalar_one()
        assert abs((datetime.now(UTC) - recorded).total_seconds()) < 15
    async with connection(migrated_database) as conn:
        await as_role(conn, tenant.institution)
        with pytest.raises(DBAPIError) as error:
            await conn.execute(
                text(
                    "UPDATE attendance_records SET marked_at = '2000-01-01' WHERE session_id = :id"
                ),
                {"id": tenant.session},
            )
        assert error.value.orig.sqlstate == "23514"


async def test_duplicate_marks_under_database_concurrency(migrated_database: str) -> None:
    async with connection(migrated_database) as conn:
        tenant = await seed(conn)
    engine = create_async_engine(migrated_database, pool_size=8, max_overflow=0)
    try:

        async def mark() -> UUID | None:
            async with engine.begin() as conn:
                await as_role(conn, tenant.institution)
                return await conn.scalar(
                    text("""
                    INSERT INTO attendance_records
                        (institution_id, user_id, session_id, status, source,
                         marked_by_user_id, manual_reason)
                    VALUES (:tenant, :user, :session, 'manual', 'manual', :user, 'test concurrency')
                    ON CONFLICT (session_id, user_id) DO NOTHING RETURNING id
                """),
                    {"tenant": tenant.institution, "user": tenant.user, "session": tenant.session},
                )

        results = await asyncio.gather(*(mark() for _ in range(32)))
        assert sum(item is not None for item in results) == 1
        async with engine.connect() as conn:
            assert (
                await conn.scalar(
                    text("SELECT count(*) FROM attendance_records WHERE session_id = :id"),
                    {"id": tenant.session},
                )
                == 1
            )
    finally:
        await engine.dispose()


async def test_audit_concurrent_hash_chain_and_timezone_stability(migrated_database: str) -> None:
    async with connection(migrated_database) as conn:
        tenant = await seed(conn)
    engine = create_async_engine(migrated_database, pool_size=4, max_overflow=0)
    try:

        async def append(number: int) -> None:
            async with engine.begin() as conn:
                await as_role(conn, tenant.institution)
                await conn.execute(
                    insert(metadata.tables["audit_logs"]).values(
                        institution_id=tenant.institution,
                        actor_user_id=tenant.user,
                        action="test.append",
                        resource_type="fixture",
                        details={"number": number},
                    )
                )

        await asyncio.gather(*(append(number) for number in range(12)))
        async with engine.begin() as conn:
            await as_role(conn, tenant.institution)
            await conn.execute(text("SET LOCAL TIME ZONE 'Asia/Kolkata'"))
            rows = (
                await conn.execute(
                    text("""
                SELECT sequence, previous_hash, entry_hash,
                       public.aifams_audit_digest(audit_logs) = entry_hash AS valid
                FROM audit_logs ORDER BY sequence
            """)
                )
            ).all()
            assert [row.sequence for row in rows] == list(range(1, 13))
            previous = "0" * 64
            for row in rows:
                assert row.previous_hash == previous and row.valid
                previous = row.entry_hash
    finally:
        await engine.dispose()


@pytest.mark.parametrize(
    "operation",
    ["UPDATE audit_logs SET action = 'tampered'", "DELETE FROM audit_logs", "TRUNCATE audit_logs"],
)
async def test_audit_is_append_only_even_for_migration_owner(
    migrated_database: str,
    operation: str,
) -> None:
    async with connection(migrated_database) as conn:
        with pytest.raises(DBAPIError) as error:
            await conn.execute(text(operation))
        assert error.value.orig.sqlstate == "42501"


async def test_runtime_cannot_forge_verification(migrated_database: str) -> None:
    async with connection(migrated_database) as conn:
        tenant = await seed(conn)
        await as_role(conn, tenant.institution)
        for table in ("verification_attempts", "liveness_events", "model_versions"):
            assert not await conn.scalar(
                text("SELECT has_table_privilege(current_user, :table, 'INSERT')"), {"table": table}
            )
        for privilege in ("UPDATE", "DELETE", "TRUNCATE"):
            assert not await conn.scalar(
                text("SELECT has_table_privilege(current_user, 'audit_logs', :privilege)"),
                {"privilege": privilege},
            )


async def test_verified_face_record_and_identity_binding(migrated_database: str) -> None:
    async with connection(migrated_database) as conn:
        tenant = await seed(conn)
        template, model, _ = await seed_template(conn, tenant)
        attempt_id = uuid4()
        await as_role(conn, tenant.institution, biometric=True)
        await conn.execute(
            insert(metadata.tables["verification_attempts"]).values(
                id=attempt_id,
                institution_id=tenant.institution,
                user_id=tenant.user,
                session_id=tenant.session,
                model_version_id=model,
                template_id=template,
                outcome="verified",
                reason_codes=[],
                threshold_snapshot={"fixture": True},
                challenge_passed=True,
                verified_at=datetime.now(UTC),
            )
        )
    async with connection(migrated_database) as conn:
        await as_role(conn, tenant.institution)
        result = await conn.execute(
            insert(metadata.tables["attendance_records"])
            .values(
                institution_id=tenant.institution,
                user_id=tenant.user,
                session_id=tenant.session,
                status="present",
                source="face",
                verification_attempt_id=attempt_id,
                verification_outcome="verified",
            )
            .returning(metadata.tables["attendance_records"].c.id)
        )
        assert result.scalar_one()
    async with connection(migrated_database) as conn:
        other_user = uuid4()
        await conn.execute(
            insert(metadata.tables["users"]).values(
                id=other_user,
                institution_id=tenant.institution,
                email=f"{other_user}@example.invalid",
                display_name="Other test user",
            )
        )
    async with connection(migrated_database) as conn:
        await as_role(conn, tenant.institution, biometric=True)
        with pytest.raises(DBAPIError) as error:
            await conn.execute(
                insert(metadata.tables["verification_attempts"]).values(
                    institution_id=tenant.institution,
                    user_id=other_user,
                    session_id=tenant.session,
                    model_version_id=model,
                    template_id=template,
                    outcome="verified",
                    reason_codes=[],
                    threshold_snapshot={},
                    challenge_passed=True,
                    verified_at=datetime.now(UTC),
                )
            )
        assert error.value.orig.sqlstate == "23503"


@pytest.mark.parametrize(
    "change",
    [{"status": "invalid"}, {"ends_at": datetime(2025, 1, 1, tzinfo=UTC)}, {"grace_minutes": -1}],
)
async def test_session_constraints_reject_invalid_values(
    migrated_database: str,
    change: dict[str, object],
) -> None:
    async with connection(migrated_database) as conn:
        tenant = await seed(conn)
    async with connection(migrated_database) as conn:
        with pytest.raises(DBAPIError) as error:
            await conn.execute(
                metadata.tables["attendance_sessions"]
                .update()
                .where(metadata.tables["attendance_sessions"].c.id == tenant.session)
                .values(**change)
            )
        assert error.value.orig.sqlstate == "23514"


async def test_guardian_required_without_guardian_consent_is_rejected(
    migrated_database: str,
) -> None:
    async with connection(migrated_database) as conn:
        tenant = await seed(conn)
        _, _, consent = await seed_template(conn, tenant)
    async with connection(migrated_database) as conn:
        with pytest.raises(DBAPIError) as error:
            await conn.execute(
                metadata.tables["biometric_consents"]
                .update()
                .where(metadata.tables["biometric_consents"].c.id == consent)
                .values(guardian_required=True)
            )
        assert error.value.orig.sqlstate == "23514"
