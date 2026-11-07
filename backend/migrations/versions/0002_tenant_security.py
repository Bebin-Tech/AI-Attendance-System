"""Force tenant isolation, separate service privileges, and protect audit history.

Revision ID: 0002
Revises: 0001
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

# Frozen list: historical migrations must not import the live application metadata.
TENANT_TABLES = (
    "academic_years",
    "anomaly_alerts",
    "api_keys",
    "attendance_correction_requests",
    "attendance_devices",
    "attendance_records",
    "attendance_sessions",
    "audit_logs",
    "batch_members",
    "batches",
    "biometric_consents",
    "biometric_templates",
    "condonation_requests",
    "consent_notices",
    "courses",
    "data_subject_requests",
    "departments",
    "device_bindings",
    "enrollments",
    "events",
    "face_enrollment_sessions",
    "faculty",
    "faculty_subjects",
    "feature_flags",
    "guardian_consents",
    "holidays",
    "idempotency_keys",
    "import_errors",
    "import_jobs",
    "leave_requests",
    "liveness_events",
    "model_versions",
    "notifications",
    "outbox_events",
    "parent_links",
    "refresh_tokens",
    "report_jobs",
    "retention_policies",
    "role_permissions",
    "roles",
    "rooms",
    "sections",
    "semesters",
    "session_qr_tokens",
    "staff",
    "students",
    "subjects",
    "system_settings",
    "timetable_entries",
    "user_roles",
    "users",
    "verification_attempts",
    "webhook_deliveries",
    "webhooks",
)

AUDIT_CHAIN = """
CREATE FUNCTION public.aifams_audit_chain() RETURNS trigger
LANGUAGE plpgsql SET search_path = pg_catalog, public AS $$
DECLARE previous_sequence bigint; previous_digest text;
BEGIN
    PERFORM pg_advisory_xact_lock(hashtextextended(NEW.institution_id::text, 0));
    SELECT sequence, entry_hash INTO previous_sequence, previous_digest
      FROM public.audit_logs WHERE institution_id = NEW.institution_id
      ORDER BY sequence DESC LIMIT 1;
    NEW.sequence := coalesce(previous_sequence, 0) + 1;
    NEW.previous_hash := coalesce(previous_digest, repeat('0', 64));
    NEW.created_at := statement_timestamp();
    NEW.updated_at := NEW.created_at;
    NEW.entry_hash := public.aifams_audit_digest(NEW);
    RETURN NEW;
END $$
"""


def upgrade() -> None:
    # Pre-provision these NOLOGIN groups in production to avoid CREATEROLE there.
    # They are retained by downgrade because groups can be shared across databases.
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aifams_app') THEN
                CREATE ROLE aifams_app NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aifams_biometric') THEN
                CREATE ROLE aifams_biometric NOLOGIN NOSUPERUSER NOBYPASSRLS
                    NOCREATEDB NOCREATEROLE;
            END IF;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname IN ('aifams_app', 'aifams_biometric')
                       AND (rolsuper OR rolbypassrls OR rolcanlogin
                            OR rolcreaterole OR rolcreatedb)) THEN
                RAISE EXCEPTION 'Unsafe AIFAMS service group attributes';
            END IF;
        END $$
    """)
    op.execute("REVOKE CREATE ON SCHEMA public FROM PUBLIC")
    op.execute("GRANT USAGE ON SCHEMA public TO aifams_app, aifams_biometric")
    for table in (*TENANT_TABLES, "institutions"):
        key = "id" if table == "institutions" else "institution_id"
        expression = f"{key} = NULLIF(current_setting('aifams.institution_id', true), '')::uuid"
        op.execute(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY')
        op.execute(f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY')
        op.execute(
            f'CREATE POLICY tenant_isolation ON "{table}" '
            f"USING ({expression}) WITH CHECK ({expression})"
        )
        op.execute(f'REVOKE ALL ON "{table}" FROM PUBLIC, aifams_app, aifams_biometric')
        if table not in {
            "biometric_templates",
            "verification_attempts",
            "liveness_events",
            "audit_logs",
            "model_versions",
            "institutions",
        }:
            op.execute(f'GRANT SELECT, INSERT, UPDATE, DELETE ON "{table}" TO aifams_app')
        if table != "audit_logs":
            op.execute(
                f'CREATE TRIGGER set_updated_at BEFORE UPDATE ON "{table}" '
                "FOR EACH ROW EXECUTE FUNCTION public.aifams_touch_updated_at()"
            )

    # Permission catalogue and model governance cannot be rewritten by ordinary API SQL.
    op.execute("REVOKE ALL ON permissions FROM PUBLIC, aifams_app, aifams_biometric")
    op.execute("GRANT SELECT ON permissions, institutions, model_versions TO aifams_app")
    # Verification decisions are only writable by the isolated biometric service.
    op.execute("GRANT SELECT ON verification_attempts, liveness_events TO aifams_app")
    op.execute("GRANT SELECT, INSERT ON audit_logs TO aifams_app, aifams_biometric")
    op.execute("""
        GRANT SELECT (id, institution_id, created_at, updated_at, user_id, consent_id,
                      model_version_id, template_version, quality_score, expires_at,
                      is_active, key_version) ON biometric_templates TO aifams_app
    """)
    op.execute("""
        GRANT SELECT ON institutions, users, consent_notices, biometric_consents,
                        guardian_consents, parent_links, model_versions,
                        attendance_sessions, attendance_devices, device_bindings
        TO aifams_biometric
    """)
    op.execute("""
        GRANT SELECT, INSERT, UPDATE, DELETE ON biometric_templates,
            face_enrollment_sessions, verification_attempts, liveness_events TO aifams_biometric
    """)
    op.execute("""
        CREATE FUNCTION public.aifams_audit_digest(public.audit_logs) RETURNS text
        LANGUAGE sql IMMUTABLE SET search_path = pg_catalog, public AS $$
            SELECT encode(sha256(convert_to((
                (to_jsonb($1) - 'entry_hash' - 'created_at' - 'updated_at') ||
                jsonb_build_object('created_at_epoch', extract(epoch from $1.created_at),
                                  'updated_at_epoch', extract(epoch from $1.updated_at))
            )::text, 'UTF8')), 'hex')
        $$
    """)
    op.execute(AUDIT_CHAIN)
    op.execute(
        "CREATE TRIGGER audit_chain BEFORE INSERT ON audit_logs "
        "FOR EACH ROW EXECUTE FUNCTION public.aifams_audit_chain()"
    )
    op.execute("""
        CREATE FUNCTION public.aifams_forbid_audit_mutation() RETURNS trigger
        LANGUAGE plpgsql AS $$ BEGIN
            RAISE EXCEPTION 'audit_logs is append-only' USING ERRCODE = '42501';
        END $$
    """)
    op.execute(
        "CREATE TRIGGER immutable_audit BEFORE UPDATE OR DELETE OR TRUNCATE ON audit_logs "
        "FOR EACH STATEMENT EXECUTE FUNCTION public.aifams_forbid_audit_mutation()"
    )
    op.execute("""
        CREATE FUNCTION public.aifams_record_timestamp() RETURNS trigger
        LANGUAGE plpgsql AS $$ BEGIN
            IF TG_OP = 'INSERT' THEN
                NEW.marked_at := statement_timestamp();
            ELSIF NEW.marked_at IS DISTINCT FROM OLD.marked_at THEN
                RAISE EXCEPTION 'Attendance timestamps cannot be changed' USING ERRCODE = '23514';
            END IF;
            RETURN NEW;
        END $$
    """)
    op.execute(
        "CREATE TRIGGER record_timestamp BEFORE INSERT OR UPDATE ON attendance_records "
        "FOR EACH ROW EXECUTE FUNCTION public.aifams_record_timestamp()"
    )
    for function in (
        "aifams_audit_chain",
        "aifams_forbid_audit_mutation",
        "aifams_touch_updated_at",
    ):
        op.execute(f"REVOKE ALL ON FUNCTION public.{function}() FROM PUBLIC")
    op.execute(
        "GRANT EXECUTE ON FUNCTION public.aifams_audit_chain(), "
        "public.aifams_touch_updated_at() TO aifams_app, aifams_biometric"
    )
    op.execute("REVOKE ALL ON FUNCTION public.aifams_record_timestamp() FROM PUBLIC")
    op.execute("GRANT EXECUTE ON FUNCTION public.aifams_record_timestamp() TO aifams_app")
    op.execute("REVOKE ALL ON FUNCTION public.aifams_audit_digest(public.audit_logs) FROM PUBLIC")
    op.execute(
        "GRANT EXECUTE ON FUNCTION public.aifams_audit_digest(public.audit_logs) "
        "TO aifams_app, aifams_biometric"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER record_timestamp ON attendance_records")
    op.execute("DROP FUNCTION public.aifams_record_timestamp()")
    op.execute("DROP TRIGGER immutable_audit ON audit_logs")
    op.execute("DROP TRIGGER audit_chain ON audit_logs")
    op.execute("DROP FUNCTION public.aifams_forbid_audit_mutation()")
    op.execute("DROP FUNCTION public.aifams_audit_chain()")
    op.execute("DROP FUNCTION public.aifams_audit_digest(public.audit_logs)")
    # Table-level REVOKE does not remove separately granted column privileges.
    op.execute("""
        REVOKE SELECT (id, institution_id, created_at, updated_at, user_id, consent_id,
                       model_version_id, template_version, quality_score, expires_at,
                       is_active, key_version) ON biometric_templates FROM aifams_app
    """)
    for table in (*TENANT_TABLES, "institutions"):
        if table != "audit_logs":
            op.execute(f'DROP TRIGGER set_updated_at ON "{table}"')
        op.execute(f'DROP POLICY tenant_isolation ON "{table}"')
        op.execute(f'ALTER TABLE "{table}" NO FORCE ROW LEVEL SECURITY')
        op.execute(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY')
        op.execute(f'REVOKE ALL ON "{table}" FROM aifams_app, aifams_biometric')
    op.execute("REVOKE ALL ON permissions FROM aifams_app, aifams_biometric")
