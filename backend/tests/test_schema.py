import runpy
from pathlib import Path

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint, inspect, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

from app.models import BiometricTemplate, metadata

REQUIRED_TABLES = set(
    """
institutions users roles permissions role_permissions user_roles departments courses
academic_years semesters sections students faculty staff subjects faculty_subjects enrollments
biometric_consents biometric_templates face_enrollment_sessions attendance_sessions
attendance_records attendance_devices attendance_correction_requests leave_requests holidays
notifications audit_logs refresh_tokens system_settings model_versions rooms timetable_entries
parent_links guardian_consents verification_attempts liveness_events device_bindings
session_qr_tokens
import_jobs import_errors report_jobs api_keys webhooks webhook_deliveries outbox_events
idempotency_keys retention_policies data_subject_requests feature_flags condonation_requests
anomaly_alerts consent_notices batches batch_members events
""".split()
)


def test_required_tables_and_primary_keys() -> None:
    assert set(metadata.tables) == REQUIRED_TABLES
    for table in metadata.tables.values():
        assert [column.name for column in table.primary_key] == ["id"]
        assert {"created_at", "updated_at"} <= set(table.c.keys())
        assert table.c.created_at.type.timezone
        if table.name not in {"institutions", "permissions"}:
            assert not table.c.institution_id.nullable


def test_every_relationship_preserves_tenant_boundary() -> None:
    for table in metadata.tables.values():
        for foreign_key in table.foreign_key_constraints:
            target = foreign_key.referred_table
            if target.name in {"institutions", "permissions"}:
                continue
            assert "institution_id" in foreign_key.column_keys, str(foreign_key)
            assert "institution_id" in [item.column.name for item in foreign_key.elements]
            assert foreign_key.ondelete == "RESTRICT"


def test_attendance_has_unconditional_session_user_uniqueness() -> None:
    constraints = metadata.tables["attendance_records"].constraints
    assert any(
        isinstance(item, UniqueConstraint)
        and list(item.columns.keys()) == ["session_id", "user_id"]
        for item in constraints
    )
    assert any(
        isinstance(item, ForeignKeyConstraint) and "verification_outcome" in item.column_keys
        for item in constraints
    )


def test_active_template_index_and_encrypted_orm_fields() -> None:
    template = metadata.tables["biometric_templates"]
    index = next(item for item in template.indexes if item.name == "uq_biometric_templates_active")
    assert index.unique
    assert (
        str(index.dialect_options["postgresql"]["where"]) == "biometric_templates.is_active IS true"
    )
    mapper = inspect(BiometricTemplate)
    for field in ("ciphertext", "wrapped_key", "nonce"):
        assert mapper.attrs[field].deferred
        assert mapper.attrs[field].raiseload
    sql = str(select(BiometricTemplate).compile(dialect=postgresql.dialect()))
    assert "ciphertext" not in sql and "wrapped_key" not in sql and "nonce" not in sql


def test_postgresql_ddl_compiles_and_constraint_names_are_unambiguous() -> None:
    names: set[str] = set()
    for table in metadata.sorted_tables:
        assert str(CreateTable(table).compile(dialect=postgresql.dialect()))
        local_names = [str(item.name) for item in table.constraints]
        assert len(local_names) == len(set(local_names))
        for index in table.indexes:
            assert str(CreateIndex(index).compile(dialect=postgresql.dialect()))
            assert str(index.name) not in names
            names.add(str(index.name))


def test_frozen_revisions_do_not_import_live_models() -> None:
    versions = Path(__file__).parents[1] / "migrations/versions"
    for path in versions.glob("*.py"):
        assert "app.models" not in path.read_text(encoding="utf-8")


def test_security_revision_covers_every_tenant_table() -> None:
    revision = Path(__file__).parents[1] / "migrations/versions/0002_tenant_security.py"
    frozen = runpy.run_path(str(revision))["TENANT_TABLES"]
    assert set(frozen) == set(metadata.tables) - {"institutions", "permissions"}
