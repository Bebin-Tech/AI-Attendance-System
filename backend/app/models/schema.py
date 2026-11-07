"""PostgreSQL schema. Relationships always include the institution boundary."""

from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
    Time,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.schema import SchemaItem
from sqlalchemy.sql.type_api import TypeEngine

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


def col(
    name: str, kind: TypeEngine[Any], *, optional: bool = False, default: str | None = None
) -> Column[Any]:
    return Column(
        name, kind, nullable=optional, server_default=text(default) if default is not None else None
    )


def label(name: str, *, optional: bool = False) -> Column[Any]:
    return col(name, String(200), optional=optional)


def stamp(name: str, *, optional: bool = False) -> Column[Any]:
    return col(name, DateTime(timezone=True), optional=optional)


def document(name: str, *, optional: bool = False) -> Column[Any]:
    return col(name, JSONB(), optional=optional)


def check(expression: str, name: str) -> CheckConstraint:
    return CheckConstraint(expression, name=name)


def states(column: str, values: str) -> CheckConstraint:
    choices = ", ".join(repr(value) for value in values.split())
    return check(f"{column} IN ({choices})", f"{column}_values")


def ref(name: str, *, optional: bool = False) -> Column[Any]:
    return col(name, Uuid(), optional=optional)


def link(column: str, target: str) -> ForeignKeyConstraint:
    return ForeignKeyConstraint(
        ["institution_id", column],
        [f"{target}.institution_id", f"{target}.id"],
        ondelete="RESTRICT",
    )


def unique(*columns: str) -> UniqueConstraint:
    return UniqueConstraint("institution_id", *columns)


def entity(name: str, *items: SchemaItem, tenant: bool = True, soft_delete: bool = False) -> Table:
    # SQLAlchemy accepts heterogeneous schema items; concrete table definitions below
    # remain the source of truth for constraints, not an ORM relationship convention.
    base: list[SchemaItem] = [
        Column("id", Uuid(), primary_key=True, server_default=text("gen_random_uuid()"))
    ]
    if tenant:
        base.extend(
            [
                Column(
                    "institution_id",
                    Uuid(),
                    ForeignKey("institutions.id", ondelete="RESTRICT"),
                    nullable=False,
                ),
            ]
        )
    base.extend(
        [
            Column(
                "created_at",
                DateTime(timezone=True),
                nullable=False,
                server_default=text("CURRENT_TIMESTAMP"),
            ),
            Column(
                "updated_at",
                DateTime(timezone=True),
                nullable=False,
                server_default=text("CURRENT_TIMESTAMP"),
            ),
        ]
    )
    if soft_delete:
        base.append(Column("deleted_at", DateTime(timezone=True)))
    table = Table(name, metadata, *base, *items)
    if tenant:
        table.append_constraint(
            UniqueConstraint("institution_id", "id", name=f"uq_{name}_tenant_id")
        )
        Index(f"ix_{name}_tenant_id", table.c.institution_id)
    return table


institutions = entity(
    "institutions",
    label("code"),
    label("name"),
    label("timezone"),
    col("enabled", Boolean(), default="true"),
    UniqueConstraint("code"),
    tenant=False,
    soft_delete=True,
)
permissions = entity(
    "permissions", label("code"), col("description", Text()), UniqueConstraint("code"), tenant=False
)
roles = entity("roles", label("code"), label("name"), unique("code"))
role_permissions = entity(
    "role_permissions",
    ref("role_id"),
    ref("permission_id"),
    link("role_id", "roles"),
    ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="RESTRICT"),
    unique("role_id", "permission_id"),
)
users = entity(
    "users",
    col("email", String(320)),
    col("display_name", String(200)),
    col("password_hash", Text(), optional=True),
    col("is_active", Boolean(), default="true"),
    col("mfa_required", Boolean(), default="false"),
    col("mfa_secret_ciphertext", LargeBinary(), optional=True),
    label("external_subject", optional=True),
    unique("email"),
    check("email = lower(email) AND position('@' in email) > 1", "email_normalized"),
    soft_delete=True,
)
departments = entity("departments", label("code"), label("name"), unique("code"), soft_delete=True)
courses = entity(
    "courses",
    ref("department_id"),
    label("code"),
    label("name"),
    link("department_id", "departments"),
    unique("code"),
    soft_delete=True,
)
academic_years = entity(
    "academic_years",
    label("name"),
    col("starts_on", Date()),
    col("ends_on", Date()),
    unique("name"),
    check("ends_on >= starts_on", "date_order"),
)
semesters = entity(
    "semesters",
    ref("course_id"),
    ref("academic_year_id"),
    col("number", Integer()),
    col("starts_on", Date()),
    col("ends_on", Date()),
    link("course_id", "courses"),
    link("academic_year_id", "academic_years"),
    unique("course_id", "academic_year_id", "number"),
    check("number > 0", "positive_number"),
    check("ends_on >= starts_on", "date_order"),
)
sections = entity(
    "sections",
    ref("semester_id"),
    label("code"),
    label("name"),
    link("semester_id", "semesters"),
    unique("semester_id", "code"),
    soft_delete=True,
)
students = entity(
    "students",
    ref("user_id"),
    ref("department_id"),
    ref("section_id"),
    label("registration_number"),
    col("graduation_date", Date(), optional=True),
    link("user_id", "users"),
    link("department_id", "departments"),
    link("section_id", "sections"),
    unique("user_id"),
    unique("registration_number"),
    soft_delete=True,
)
faculty = entity(
    "faculty",
    ref("user_id"),
    ref("department_id"),
    label("employee_number"),
    link("user_id", "users"),
    link("department_id", "departments"),
    unique("user_id"),
    unique("employee_number"),
    soft_delete=True,
)
staff = entity(
    "staff",
    ref("user_id"),
    ref("department_id", optional=True),
    label("employee_number"),
    link("user_id", "users"),
    link("department_id", "departments"),
    unique("user_id"),
    unique("employee_number"),
    soft_delete=True,
)
user_roles = entity(
    "user_roles",
    ref("user_id"),
    ref("role_id"),
    ref("department_id", optional=True),
    ref("section_id", optional=True),
    link("user_id", "users"),
    link("role_id", "roles"),
    link("department_id", "departments"),
    link("section_id", "sections"),
    check("section_id IS NULL OR department_id IS NOT NULL", "scope_hierarchy"),
)
Index(
    "uq_user_roles_scope",
    user_roles.c.institution_id,
    user_roles.c.user_id,
    user_roles.c.role_id,
    user_roles.c.department_id,
    user_roles.c.section_id,
    unique=True,
    postgresql_nulls_not_distinct=True,
)
subjects = entity(
    "subjects",
    ref("department_id"),
    label("code"),
    label("name"),
    link("department_id", "departments"),
    unique("code"),
    soft_delete=True,
)
faculty_subjects = entity(
    "faculty_subjects",
    ref("faculty_id"),
    ref("subject_id"),
    ref("section_id"),
    link("faculty_id", "faculty"),
    link("subject_id", "subjects"),
    link("section_id", "sections"),
    unique("faculty_id", "subject_id", "section_id"),
)
enrollments = entity(
    "enrollments",
    ref("student_id"),
    ref("subject_id"),
    ref("section_id"),
    col("starts_on", Date()),
    col("ends_on", Date(), optional=True),
    link("student_id", "students"),
    link("subject_id", "subjects"),
    link("section_id", "sections"),
    check("ends_on IS NULL OR ends_on >= starts_on", "date_order"),
    unique("student_id", "subject_id", "section_id", "starts_on"),
)
rooms = entity(
    "rooms",
    label("code"),
    label("name"),
    col("capacity", Integer()),
    ref("department_id", optional=True),
    link("department_id", "departments"),
    unique("code"),
    check("capacity > 0", "positive_capacity"),
    soft_delete=True,
)
batches = entity(
    "batches",
    ref("section_id"),
    label("name"),
    states("kind", "batch lab_group"),
    label("kind"),
    link("section_id", "sections"),
    unique("section_id", "name"),
)
batch_members = entity(
    "batch_members",
    ref("batch_id"),
    ref("student_id"),
    link("batch_id", "batches"),
    link("student_id", "students"),
    unique("batch_id", "student_id"),
)
holidays = entity(
    "holidays",
    label("name"),
    col("starts_on", Date()),
    col("ends_on", Date()),
    ref("department_id", optional=True),
    link("department_id", "departments"),
    check("ends_on >= starts_on", "date_order"),
)
events = entity(
    "events",
    label("name"),
    stamp("starts_at"),
    stamp("ends_at"),
    ref("room_id", optional=True),
    link("room_id", "rooms"),
    check("ends_at > starts_at", "time_order"),
)
timetable_entries = entity(
    "timetable_entries",
    ref("academic_year_id"),
    ref("section_id"),
    ref("subject_id"),
    ref("faculty_id"),
    ref("room_id"),
    col("weekday", Integer()),
    col("starts_at", Time()),
    col("ends_at", Time()),
    col("valid_from", Date()),
    col("valid_until", Date()),
    link("academic_year_id", "academic_years"),
    link("section_id", "sections"),
    link("subject_id", "subjects"),
    link("faculty_id", "faculty"),
    link("room_id", "rooms"),
    check("weekday BETWEEN 0 AND 6", "weekday_range"),
    check("ends_at > starts_at", "time_order"),
    check("valid_until >= valid_from", "date_order"),
)

parent_links = entity(
    "parent_links",
    ref("parent_user_id"),
    ref("student_id"),
    link("parent_user_id", "users"),
    link("student_id", "students"),
    label("relationship"),
    stamp("consented_at", optional=True),
    stamp("revoked_at", optional=True),
    unique("parent_user_id", "student_id"),
)
guardian_consents = entity(
    "guardian_consents",
    ref("parent_link_id"),
    label("notice_version"),
    label("purpose"),
    stamp("granted_at"),
    stamp("withdrawn_at", optional=True),
    link("parent_link_id", "parent_links"),
)
consent_notices = entity(
    "consent_notices",
    label("version"),
    label("purpose"),
    label("language"),
    col("text", Text()),
    col("retention_days", Integer()),
    unique("version", "purpose", "language"),
    check("retention_days > 0", "positive_retention"),
)
biometric_consents = entity(
    "biometric_consents",
    ref("user_id"),
    ref("notice_id"),
    stamp("granted_at"),
    stamp("withdrawn_at", optional=True),
    label("ip_address"),
    label("device_reference"),
    label("language"),
    col("guardian_required", Boolean(), default="false"),
    ref("guardian_consent_id", optional=True),
    link("user_id", "users"),
    link("notice_id", "consent_notices"),
    link("guardian_consent_id", "guardian_consents"),
    check("NOT guardian_required OR guardian_consent_id IS NOT NULL", "guardian_required"),
    check("withdrawn_at IS NULL OR withdrawn_at >= granted_at", "withdrawal_order"),
)
model_versions = entity(
    "model_versions",
    label("name"),
    label("version"),
    col("checksum_sha256", String(64)),
    col("license", Text()),
    label("artifact_reference"),
    document("evaluation_metrics"),
    label("rollout_status"),
    states("rollout_status", "candidate shadow active retired blocked"),
    check("checksum_sha256 ~ '^[0-9a-f]{64}$'", "valid_checksum"),
    unique("name", "version"),
)
biometric_templates = entity(
    "biometric_templates",
    ref("user_id"),
    ref("consent_id"),
    ref("model_version_id"),
    col("template_version", Integer()),
    col("quality_score", Numeric(6, 5)),
    stamp("expires_at"),
    col("is_active", Boolean(), default="true"),
    label("key_version"),
    col("ciphertext", LargeBinary()),
    col("wrapped_key", LargeBinary()),
    col("nonce", LargeBinary()),
    link("user_id", "users"),
    link("consent_id", "biometric_consents"),
    link("model_version_id", "model_versions"),
    # Ensure a user's template cannot reference another user's consent.
    ForeignKeyConstraint(
        ["institution_id", "consent_id", "user_id"],
        [
            "biometric_consents.institution_id",
            "biometric_consents.id",
            "biometric_consents.user_id",
        ],
        ondelete="RESTRICT",
    ),
    check("template_version > 0", "positive_version"),
    check("quality_score BETWEEN 0 AND 1", "quality_range"),
    check("octet_length(nonce) = 12", "gcm_nonce_length"),
    check("octet_length(ciphertext) >= 16", "gcm_tag_present"),
    check("octet_length(wrapped_key) > 0", "wrapped_key_present"),
    check("expires_at > created_at", "expiry_order"),
)
biometric_consents.append_constraint(
    UniqueConstraint("institution_id", "id", "user_id", name="uq_consent_identity")
)
Index(
    "uq_biometric_templates_active",
    biometric_templates.c.institution_id,
    biometric_templates.c.user_id,
    biometric_templates.c.model_version_id,
    unique=True,
    postgresql_where=biometric_templates.c.is_active.is_(True),
)
face_enrollment_sessions = entity(
    "face_enrollment_sessions",
    ref("user_id"),
    ref("consent_id"),
    label("status"),
    document("challenge"),
    stamp("expires_at"),
    col("accepted_samples", Integer(), default="0"),
    link("user_id", "users"),
    link("consent_id", "biometric_consents"),
    states("status", "pending capturing completed rejected expired"),
    check("accepted_samples BETWEEN 0 AND 8", "sample_count"),
    check("expires_at > created_at", "expiry_order"),
)

attendance_devices = entity(
    "attendance_devices",
    label("name"),
    label("kind"),
    label("public_key_fingerprint"),
    stamp("revoked_at", optional=True),
    col("kiosk_enabled", Boolean(), default="false"),
    states("kind", "android web kiosk"),
    unique("public_key_fingerprint"),
)
device_bindings = entity(
    "device_bindings",
    ref("user_id"),
    ref("device_id"),
    col("is_primary", Boolean(), default="false"),
    stamp("approved_at", optional=True),
    stamp("revoked_at", optional=True),
    link("user_id", "users"),
    link("device_id", "attendance_devices"),
)
Index(
    "uq_device_bindings_primary",
    device_bindings.c.institution_id,
    device_bindings.c.user_id,
    unique=True,
    postgresql_where=text("is_primary AND revoked_at IS NULL"),
)
attendance_sessions = entity(
    "attendance_sessions",
    ref("academic_year_id"),
    ref("department_id"),
    ref("course_id", optional=True),
    ref("semester_id", optional=True),
    ref("section_id", optional=True),
    ref("subject_id", optional=True),
    ref("faculty_id", optional=True),
    ref("room_id", optional=True),
    ref("event_id", optional=True),
    ref("timetable_entry_id", optional=True),
    label("attendance_type"),
    col("session_date", Date()),
    stamp("starts_at"),
    stamp("ends_at"),
    col("grace_minutes", Integer(), default="0"),
    label("status"),
    label("mode"),
    document("policy_snapshot"),
    link("academic_year_id", "academic_years"),
    link("department_id", "departments"),
    link("course_id", "courses"),
    link("semester_id", "semesters"),
    link("section_id", "sections"),
    link("subject_id", "subjects"),
    link("faculty_id", "faculty"),
    link("room_id", "rooms"),
    link("event_id", "events"),
    link("timetable_entry_id", "timetable_entries"),
    states(
        "attendance_type", "student faculty staff class event laboratory exam_hall workshop seminar"
    ),
    states("status", "scheduled open paused closed cancelled"),
    states("mode", "face qr_face manual"),
    check("ends_at > starts_at", "time_order"),
    check("grace_minutes >= 0", "nonnegative_grace"),
)
session_qr_tokens = entity(
    "session_qr_tokens",
    ref("session_id"),
    col("token_hash", String(64)),
    stamp("valid_from"),
    stamp("expires_at"),
    link("session_id", "attendance_sessions"),
    unique("token_hash"),
    check("expires_at > valid_from", "validity_order"),
)
verification_attempts = entity(
    "verification_attempts",
    ref("user_id"),
    ref("session_id"),
    ref("model_version_id"),
    ref("template_id", optional=True),
    ref("device_id", optional=True),
    label("outcome"),
    col("similarity_score", Numeric(8, 6), optional=True),
    col("confidence", Numeric(6, 5), optional=True),
    document("reason_codes"),
    document("threshold_snapshot"),
    col("challenge_passed", Boolean()),
    stamp("verified_at", optional=True),
    link("user_id", "users"),
    link("session_id", "attendance_sessions"),
    link("model_version_id", "model_versions"),
    link("template_id", "biometric_templates"),
    link("device_id", "attendance_devices"),
    states("outcome", "verified rejected manual_review"),
    check("confidence IS NULL OR confidence BETWEEN 0 AND 1", "confidence_range"),
    check(
        "outcome <> 'verified' OR (challenge_passed AND verified_at IS NOT NULL "
        "AND template_id IS NOT NULL)",
        "verified_evidence",
    ),
)
verification_attempts.append_constraint(
    UniqueConstraint(
        "institution_id", "id", "user_id", "session_id", "outcome", name="uq_verification_identity"
    )
)
liveness_events = entity(
    "liveness_events",
    ref("verification_attempt_id", optional=True),
    ref("enrollment_session_id", optional=True),
    label("challenge_type"),
    col("passed", Boolean()),
    document("reason_codes"),
    link("verification_attempt_id", "verification_attempts"),
    link("enrollment_session_id", "face_enrollment_sessions"),
    check("num_nonnulls(verification_attempt_id, enrollment_session_id) = 1", "one_parent"),
)
attendance_records = entity(
    "attendance_records",
    ref("session_id"),
    ref("user_id"),
    label("status"),
    label("source"),
    col("marked_at", DateTime(timezone=True), default="CURRENT_TIMESTAMP"),
    ref("marked_by_user_id", optional=True),
    col("manual_reason", Text(), optional=True),
    ref("verification_attempt_id", optional=True),
    label("verification_outcome", optional=True),
    link("session_id", "attendance_sessions"),
    link("user_id", "users"),
    link("marked_by_user_id", "users"),
    ForeignKeyConstraint(
        [
            "institution_id",
            "verification_attempt_id",
            "user_id",
            "session_id",
            "verification_outcome",
        ],
        [
            "verification_attempts.institution_id",
            "verification_attempts.id",
            "verification_attempts.user_id",
            "verification_attempts.session_id",
            "verification_attempts.outcome",
        ],
        ondelete="RESTRICT",
    ),
    UniqueConstraint("session_id", "user_id", name="uq_attendance_session_user"),
    states(
        "status", "present absent late half_day on_duty leave holiday excused pending_review manual"
    ),
    states("source", "face manual policy"),
    check(
        "source <> 'face' OR (verification_attempt_id IS NOT NULL "
        "AND verification_outcome IS NOT NULL AND verification_outcome = 'verified' "
        "AND status IN ('present', 'late'))",
        "face_requires_verified",
    ),
    check(
        "source = 'face' OR (verification_attempt_id IS NULL AND verification_outcome IS NULL)",
        "verification_only_for_face",
    ),
    check(
        "source <> 'manual' OR (marked_by_user_id IS NOT NULL "
        "AND manual_reason IS NOT NULL AND length(trim(manual_reason)) > 0)",
        "manual_reason_required",
    ),
    check(
        "source <> 'policy' OR status IN "
        "('absent', 'on_duty', 'leave', 'holiday', 'excused', 'pending_review')",
        "policy_not_present",
    ),
)
attendance_correction_requests = entity(
    "attendance_correction_requests",
    ref("record_id"),
    ref("requested_by_user_id"),
    col("reason", Text()),
    label("requested_status"),
    label("status"),
    label("evidence_reference", optional=True),
    ref("decided_by_user_id", optional=True),
    stamp("decided_at", optional=True),
    link("record_id", "attendance_records"),
    link("requested_by_user_id", "users"),
    link("decided_by_user_id", "users"),
    states("status", "pending approved rejected cancelled"),
    check("length(trim(reason)) > 0", "reason_required"),
    check(
        "status NOT IN ('approved', 'rejected') OR "
        "(decided_by_user_id IS NOT NULL AND decided_at IS NOT NULL)",
        "decision_evidence",
    ),
)
leave_requests = entity(
    "leave_requests",
    ref("user_id"),
    label("kind"),
    col("starts_on", Date()),
    col("ends_on", Date()),
    col("reason", Text()),
    label("status"),
    label("evidence_reference", optional=True),
    ref("decided_by_user_id", optional=True),
    stamp("decided_at", optional=True),
    link("user_id", "users"),
    link("decided_by_user_id", "users"),
    states("kind", "leave on_duty"),
    states("status", "pending approved rejected cancelled"),
    check("ends_on >= starts_on", "date_order"),
    check("length(trim(reason)) > 0", "reason_required"),
)
condonation_requests = entity(
    "condonation_requests",
    ref("student_id"),
    ref("semester_id"),
    col("reason", Text()),
    label("status"),
    ref("decided_by_user_id", optional=True),
    stamp("decided_at", optional=True),
    link("student_id", "students"),
    link("semester_id", "semesters"),
    link("decided_by_user_id", "users"),
    states("status", "pending approved rejected cancelled"),
    check("length(trim(reason)) > 0", "reason_required"),
)
anomaly_alerts = entity(
    "anomaly_alerts",
    ref("user_id", optional=True),
    ref("session_id", optional=True),
    label("code"),
    label("severity"),
    label("status"),
    document("details"),
    link("user_id", "users"),
    link("session_id", "attendance_sessions"),
    states("severity", "low medium high critical"),
    states("status", "open acknowledged resolved dismissed"),
)

notifications = entity(
    "notifications",
    ref("user_id"),
    label("kind"),
    document("content"),
    stamp("read_at", optional=True),
    link("user_id", "users"),
)
outbox_events = entity(
    "outbox_events",
    label("event_type"),
    ref("aggregate_id"),
    document("payload"),
    stamp("available_at"),
    stamp("published_at", optional=True),
    col("attempts", Integer(), default="0"),
    check("attempts >= 0", "nonnegative_attempts"),
)
Index(
    "ix_outbox_pending",
    outbox_events.c.available_at,
    outbox_events.c.institution_id,
    postgresql_where=outbox_events.c.published_at.is_(None),
)
refresh_tokens = entity(
    "refresh_tokens",
    ref("user_id"),
    ref("family_id"),
    col("token_hash", String(64)),
    stamp("expires_at"),
    stamp("used_at", optional=True),
    stamp("revoked_at", optional=True),
    link("user_id", "users"),
    unique("token_hash"),
    check("expires_at > created_at", "expiry_order"),
)
system_settings = entity("system_settings", label("key"), document("value"), unique("key"))
feature_flags = entity(
    "feature_flags",
    label("key"),
    col("enabled", Boolean(), default="false"),
    document("configuration"),
    unique("key"),
)
retention_policies = entity(
    "retention_policies",
    label("data_category"),
    col("retention_days", Integer()),
    label("trigger"),
    unique("data_category"),
    check("retention_days > 0", "positive_retention"),
)
data_subject_requests = entity(
    "data_subject_requests",
    ref("user_id"),
    label("kind"),
    label("status"),
    stamp("completed_at", optional=True),
    link("user_id", "users"),
    states("kind", "export delete_biometrics delete_account withdraw_consent"),
    states("status", "pending processing completed rejected"),
)
import_jobs = entity(
    "import_jobs",
    ref("requested_by_user_id"),
    label("kind"),
    label("status"),
    col("dry_run", Boolean()),
    col("file_sha256", String(64)),
    col("total_rows", Integer(), default="0"),
    col("error_rows", Integer(), default="0"),
    link("requested_by_user_id", "users"),
    states("status", "pending validating validated applied failed rolled_back"),
    check("total_rows >= 0 AND error_rows BETWEEN 0 AND total_rows", "row_counts"),
)
import_errors = entity(
    "import_errors",
    ref("import_job_id"),
    col("row_number", Integer()),
    label("field"),
    label("code"),
    col("message", Text()),
    link("import_job_id", "import_jobs"),
    check("row_number > 0", "positive_row"),
)
report_jobs = entity(
    "report_jobs",
    ref("requested_by_user_id"),
    label("kind"),
    label("format"),
    label("status"),
    document("filters"),
    label("object_reference", optional=True),
    stamp("expires_at", optional=True),
    link("requested_by_user_id", "users"),
    states("format", "csv xlsx pdf"),
    states("status", "pending processing completed failed expired"),
)
api_keys = entity(
    "api_keys",
    ref("created_by_user_id"),
    label("name"),
    col("key_hash", String(64)),
    document("scopes"),
    stamp("expires_at"),
    stamp("revoked_at", optional=True),
    link("created_by_user_id", "users"),
    unique("key_hash"),
)
webhooks = entity(
    "webhooks",
    ref("created_by_user_id"),
    col("url", Text()),
    col("signing_secret_ciphertext", LargeBinary()),
    document("event_types"),
    col("enabled", Boolean(), default="false"),
    link("created_by_user_id", "users"),
    check("url LIKE 'https://%'", "https_required"),
)
webhook_deliveries = entity(
    "webhook_deliveries",
    ref("webhook_id"),
    ref("outbox_event_id"),
    label("status"),
    col("attempts", Integer(), default="0"),
    stamp("next_attempt_at"),
    col("last_http_status", Integer(), optional=True),
    link("webhook_id", "webhooks"),
    link("outbox_event_id", "outbox_events"),
    unique("webhook_id", "outbox_event_id"),
    states("status", "pending delivered failed"),
    check("attempts >= 0", "nonnegative_attempts"),
)
idempotency_keys = entity(
    "idempotency_keys",
    ref("user_id"),
    col("key_hash", String(64)),
    label("operation"),
    col("request_hash", String(64)),
    col("response_status", Integer(), optional=True),
    document("response", optional=True),
    stamp("expires_at"),
    link("user_id", "users"),
    unique("user_id", "operation", "key_hash"),
)
audit_logs = entity(
    "audit_logs",
    ref("actor_user_id", optional=True),
    label("action"),
    label("resource_type"),
    ref("resource_id", optional=True),
    document("details"),
    col("sequence", BigInteger()),
    col("previous_hash", String(64)),
    col("entry_hash", String(64)),
    link("actor_user_id", "users"),
    unique("sequence"),
    check("sequence > 0", "positive_sequence"),
    check("previous_hash ~ '^[0-9a-f]{64}$' AND entry_hash ~ '^[0-9a-f]{64}$'", "hash_format"),
)

# Index referencing columns for tenant-scoped lookups and FK validation.
for table in metadata.tables.values():
    if "institution_id" not in table.c:
        continue
    for column in table.c:
        if column.name.endswith("_id") and column.name not in {"institution_id", "id"}:
            Index(f"ix_{table.name}_{column.name}", table.c.institution_id, column)
Index(
    "ix_sessions_tenant_date",
    attendance_sessions.c.institution_id,
    attendance_sessions.c.session_date,
)
Index(
    "ix_records_tenant_user_time",
    attendance_records.c.institution_id,
    attendance_records.c.user_id,
    attendance_records.c.marked_at,
)

# Same-tenant references must also match the verified person's identity/model.
biometric_templates.append_constraint(
    UniqueConstraint(
        "institution_id", "id", "user_id", "model_version_id", name="uq_template_identity"
    )
)
verification_attempts.append_constraint(
    ForeignKeyConstraint(
        ["institution_id", "template_id", "user_id", "model_version_id"],
        [
            "biometric_templates.institution_id",
            "biometric_templates.id",
            "biometric_templates.user_id",
            "biometric_templates.model_version_id",
        ],
        ondelete="RESTRICT",
    )
)
face_enrollment_sessions.append_constraint(
    ForeignKeyConstraint(
        ["institution_id", "consent_id", "user_id"],
        [
            "biometric_consents.institution_id",
            "biometric_consents.id",
            "biometric_consents.user_id",
        ],
        ondelete="RESTRICT",
    )
)
