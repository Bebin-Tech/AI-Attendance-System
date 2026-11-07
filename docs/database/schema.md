# Schema dictionary

Generated from SQLAlchemy metadata. Historical migrations are frozen separately.

## academic_years

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| name | VARCHAR(200) | no | — |
| starts_on | DATE | no | — |
| ends_on | DATE | no | — |

Constraints:

- `ck_academic_years_date_order` (CheckConstraint): ends_on >= starts_on
- `fk_academic_years_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_academic_years` (PrimaryKeyConstraint): id
- `uq_academic_years_institution_id_name` (UniqueConstraint): institution_id, name
- `uq_academic_years_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_academic_years_tenant_id` (institution_id)

## anomaly_alerts

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | yes | — |
| session_id | UUID | yes | — |
| code | VARCHAR(200) | no | — |
| severity | VARCHAR(200) | no | — |
| status | VARCHAR(200) | no | — |
| details | JSONB | no | — |

Constraints:

- `ck_anomaly_alerts_severity_values` (CheckConstraint): severity IN ('low', 'medium', 'high', 'critical')
- `ck_anomaly_alerts_status_values` (CheckConstraint): status IN ('open', 'acknowledged', 'resolved', 'dismissed')
- `fk_anomaly_alerts_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_anomaly_alerts_institution_id_session_id_attendance_sessions` (ForeignKeyConstraint): institution_id, session_id
- `fk_anomaly_alerts_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_anomaly_alerts` (PrimaryKeyConstraint): id
- `uq_anomaly_alerts_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_anomaly_alerts_session_id` (institution_id, session_id)
- `ix_anomaly_alerts_tenant_id` (institution_id)
- `ix_anomaly_alerts_user_id` (institution_id, user_id)

## api_keys

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| created_by_user_id | UUID | no | — |
| name | VARCHAR(200) | no | — |
| key_hash | VARCHAR(64) | no | — |
| scopes | JSONB | no | — |
| expires_at | TIMESTAMP WITH TIME ZONE | no | — |
| revoked_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `fk_api_keys_institution_id_created_by_user_id_users` (ForeignKeyConstraint): institution_id, created_by_user_id
- `fk_api_keys_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_api_keys` (PrimaryKeyConstraint): id
- `uq_api_keys_institution_id_key_hash` (UniqueConstraint): institution_id, key_hash
- `uq_api_keys_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_api_keys_created_by_user_id` (institution_id, created_by_user_id)
- `ix_api_keys_tenant_id` (institution_id)

## attendance_correction_requests

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| record_id | UUID | no | — |
| requested_by_user_id | UUID | no | — |
| reason | TEXT | no | — |
| requested_status | VARCHAR(200) | no | — |
| status | VARCHAR(200) | no | — |
| evidence_reference | VARCHAR(200) | yes | — |
| decided_by_user_id | UUID | yes | — |
| decided_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `ck_attendance_correction_requests_decision_evidence` (CheckConstraint): status NOT IN ('approved', 'rejected') OR (decided_by_user_id IS NOT NULL AND decided_at IS NOT NULL)
- `ck_attendance_correction_requests_reason_required` (CheckConstraint): length(trim(reason)) > 0
- `ck_attendance_correction_requests_status_values` (CheckConstraint): status IN ('pending', 'approved', 'rejected', 'cancelled')
- `fk_attendance_correction_requests_institution_id_decided_by_user_id_users` (ForeignKeyConstraint): institution_id, decided_by_user_id
- `fk_attendance_correction_requests_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_attendance_correction_requests_institution_id_record_id_attendance_records` (ForeignKeyConstraint): institution_id, record_id
- `fk_attendance_correction_requests_institution_id_requested_by_user_id_users` (ForeignKeyConstraint): institution_id, requested_by_user_id
- `pk_attendance_correction_requests` (PrimaryKeyConstraint): id
- `uq_attendance_correction_requests_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_attendance_correction_requests_decided_by_user_id` (institution_id, decided_by_user_id)
- `ix_attendance_correction_requests_record_id` (institution_id, record_id)
- `ix_attendance_correction_requests_requested_by_user_id` (institution_id, requested_by_user_id)
- `ix_attendance_correction_requests_tenant_id` (institution_id)

## attendance_devices

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| name | VARCHAR(200) | no | — |
| kind | VARCHAR(200) | no | — |
| public_key_fingerprint | VARCHAR(200) | no | — |
| revoked_at | TIMESTAMP WITH TIME ZONE | yes | — |
| kiosk_enabled | BOOLEAN | no | false |

Constraints:

- `ck_attendance_devices_kind_values` (CheckConstraint): kind IN ('android', 'web', 'kiosk')
- `fk_attendance_devices_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_attendance_devices` (PrimaryKeyConstraint): id
- `uq_attendance_devices_institution_id_public_key_fingerprint` (UniqueConstraint): institution_id, public_key_fingerprint
- `uq_attendance_devices_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_attendance_devices_tenant_id` (institution_id)

## attendance_records

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| session_id | UUID | no | — |
| user_id | UUID | no | — |
| status | VARCHAR(200) | no | — |
| source | VARCHAR(200) | no | — |
| marked_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| marked_by_user_id | UUID | yes | — |
| manual_reason | TEXT | yes | — |
| verification_attempt_id | UUID | yes | — |
| verification_outcome | VARCHAR(200) | yes | — |

Constraints:

- `ck_attendance_records_face_requires_verified` (CheckConstraint): source <> 'face' OR (verification_attempt_id IS NOT NULL AND verification_outcome IS NOT NULL AND verification_outcome = 'verified' AND status IN ('present', 'late'))
- `ck_attendance_records_manual_reason_required` (CheckConstraint): source <> 'manual' OR (marked_by_user_id IS NOT NULL AND manual_reason IS NOT NULL AND length(trim(manual_reason)) > 0)
- `ck_attendance_records_policy_not_present` (CheckConstraint): source <> 'policy' OR status IN ('absent', 'on_duty', 'leave', 'holiday', 'excused', 'pending_review')
- `ck_attendance_records_source_values` (CheckConstraint): source IN ('face', 'manual', 'policy')
- `ck_attendance_records_status_values` (CheckConstraint): status IN ('present', 'absent', 'late', 'half_day', 'on_duty', 'leave', 'holiday', 'excused', 'pending_review', 'manual')
- `ck_attendance_records_verification_only_for_face` (CheckConstraint): source = 'face' OR (verification_attempt_id IS NULL AND verification_outcome IS NULL)
- `fk_attendance_records_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_attendance_records_institution_id_marked_by_user_id_users` (ForeignKeyConstraint): institution_id, marked_by_user_id
- `fk_attendance_records_institution_id_session_id_attendance_sessions` (ForeignKeyConstraint): institution_id, session_id
- `fk_attendance_records_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `fk_attendance_records_institution_id_verification_attempt_id_user_id_session_id_verification_outcome_verification_attempts` (ForeignKeyConstraint): institution_id, verification_attempt_id, user_id, session_id, verification_outcome
- `pk_attendance_records` (PrimaryKeyConstraint): id
- `uq_attendance_records_tenant_id` (UniqueConstraint): institution_id, id
- `uq_attendance_session_user` (UniqueConstraint): session_id, user_id

Indexes:

- `ix_attendance_records_marked_by_user_id` (institution_id, marked_by_user_id)
- `ix_attendance_records_session_id` (institution_id, session_id)
- `ix_attendance_records_tenant_id` (institution_id)
- `ix_attendance_records_user_id` (institution_id, user_id)
- `ix_attendance_records_verification_attempt_id` (institution_id, verification_attempt_id)
- `ix_records_tenant_user_time` (institution_id, user_id, marked_at)

## attendance_sessions

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| academic_year_id | UUID | no | — |
| department_id | UUID | no | — |
| course_id | UUID | yes | — |
| semester_id | UUID | yes | — |
| section_id | UUID | yes | — |
| subject_id | UUID | yes | — |
| faculty_id | UUID | yes | — |
| room_id | UUID | yes | — |
| event_id | UUID | yes | — |
| timetable_entry_id | UUID | yes | — |
| attendance_type | VARCHAR(200) | no | — |
| session_date | DATE | no | — |
| starts_at | TIMESTAMP WITH TIME ZONE | no | — |
| ends_at | TIMESTAMP WITH TIME ZONE | no | — |
| grace_minutes | INTEGER | no | 0 |
| status | VARCHAR(200) | no | — |
| mode | VARCHAR(200) | no | — |
| policy_snapshot | JSONB | no | — |

Constraints:

- `ck_attendance_sessions_attendance_type_values` (CheckConstraint): attendance_type IN ('student', 'faculty', 'staff', 'class', 'event', 'laboratory', 'exam_hall', 'workshop', 'seminar')
- `ck_attendance_sessions_mode_values` (CheckConstraint): mode IN ('face', 'qr_face', 'manual')
- `ck_attendance_sessions_nonnegative_grace` (CheckConstraint): grace_minutes >= 0
- `ck_attendance_sessions_status_values` (CheckConstraint): status IN ('scheduled', 'open', 'paused', 'closed', 'cancelled')
- `ck_attendance_sessions_time_order` (CheckConstraint): ends_at > starts_at
- `fk_attendance_sessions_institution_id_academic_year_id_academic_years` (ForeignKeyConstraint): institution_id, academic_year_id
- `fk_attendance_sessions_institution_id_course_id_courses` (ForeignKeyConstraint): institution_id, course_id
- `fk_attendance_sessions_institution_id_department_id_departments` (ForeignKeyConstraint): institution_id, department_id
- `fk_attendance_sessions_institution_id_event_id_events` (ForeignKeyConstraint): institution_id, event_id
- `fk_attendance_sessions_institution_id_faculty_id_faculty` (ForeignKeyConstraint): institution_id, faculty_id
- `fk_attendance_sessions_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_attendance_sessions_institution_id_room_id_rooms` (ForeignKeyConstraint): institution_id, room_id
- `fk_attendance_sessions_institution_id_section_id_sections` (ForeignKeyConstraint): institution_id, section_id
- `fk_attendance_sessions_institution_id_semester_id_semesters` (ForeignKeyConstraint): institution_id, semester_id
- `fk_attendance_sessions_institution_id_subject_id_subjects` (ForeignKeyConstraint): institution_id, subject_id
- `fk_attendance_sessions_institution_id_timetable_entry_id_timetable_entries` (ForeignKeyConstraint): institution_id, timetable_entry_id
- `pk_attendance_sessions` (PrimaryKeyConstraint): id
- `uq_attendance_sessions_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_attendance_sessions_academic_year_id` (institution_id, academic_year_id)
- `ix_attendance_sessions_course_id` (institution_id, course_id)
- `ix_attendance_sessions_department_id` (institution_id, department_id)
- `ix_attendance_sessions_event_id` (institution_id, event_id)
- `ix_attendance_sessions_faculty_id` (institution_id, faculty_id)
- `ix_attendance_sessions_room_id` (institution_id, room_id)
- `ix_attendance_sessions_section_id` (institution_id, section_id)
- `ix_attendance_sessions_semester_id` (institution_id, semester_id)
- `ix_attendance_sessions_subject_id` (institution_id, subject_id)
- `ix_attendance_sessions_tenant_id` (institution_id)
- `ix_attendance_sessions_timetable_entry_id` (institution_id, timetable_entry_id)
- `ix_sessions_tenant_date` (institution_id, session_date)

## audit_logs

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| actor_user_id | UUID | yes | — |
| action | VARCHAR(200) | no | — |
| resource_type | VARCHAR(200) | no | — |
| resource_id | UUID | yes | — |
| details | JSONB | no | — |
| sequence | BIGINT | no | — |
| previous_hash | VARCHAR(64) | no | — |
| entry_hash | VARCHAR(64) | no | — |

Constraints:

- `ck_audit_logs_hash_format` (CheckConstraint): previous_hash ~ '^[0-9a-f]{64}$' AND entry_hash ~ '^[0-9a-f]{64}$'
- `ck_audit_logs_positive_sequence` (CheckConstraint): sequence > 0
- `fk_audit_logs_institution_id_actor_user_id_users` (ForeignKeyConstraint): institution_id, actor_user_id
- `fk_audit_logs_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_audit_logs` (PrimaryKeyConstraint): id
- `uq_audit_logs_institution_id_sequence` (UniqueConstraint): institution_id, sequence
- `uq_audit_logs_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_audit_logs_actor_user_id` (institution_id, actor_user_id)
- `ix_audit_logs_resource_id` (institution_id, resource_id)
- `ix_audit_logs_tenant_id` (institution_id)

## batch_members

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| batch_id | UUID | no | — |
| student_id | UUID | no | — |

Constraints:

- `fk_batch_members_institution_id_batch_id_batches` (ForeignKeyConstraint): institution_id, batch_id
- `fk_batch_members_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_batch_members_institution_id_student_id_students` (ForeignKeyConstraint): institution_id, student_id
- `pk_batch_members` (PrimaryKeyConstraint): id
- `uq_batch_members_institution_id_batch_id_student_id` (UniqueConstraint): institution_id, batch_id, student_id
- `uq_batch_members_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_batch_members_batch_id` (institution_id, batch_id)
- `ix_batch_members_student_id` (institution_id, student_id)
- `ix_batch_members_tenant_id` (institution_id)

## batches

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| section_id | UUID | no | — |
| name | VARCHAR(200) | no | — |
| kind | VARCHAR(200) | no | — |

Constraints:

- `ck_batches_kind_values` (CheckConstraint): kind IN ('batch', 'lab_group')
- `fk_batches_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_batches_institution_id_section_id_sections` (ForeignKeyConstraint): institution_id, section_id
- `pk_batches` (PrimaryKeyConstraint): id
- `uq_batches_institution_id_section_id_name` (UniqueConstraint): institution_id, section_id, name
- `uq_batches_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_batches_section_id` (institution_id, section_id)
- `ix_batches_tenant_id` (institution_id)

## biometric_consents

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | no | — |
| notice_id | UUID | no | — |
| granted_at | TIMESTAMP WITH TIME ZONE | no | — |
| withdrawn_at | TIMESTAMP WITH TIME ZONE | yes | — |
| ip_address | VARCHAR(200) | no | — |
| device_reference | VARCHAR(200) | no | — |
| language | VARCHAR(200) | no | — |
| guardian_required | BOOLEAN | no | false |
| guardian_consent_id | UUID | yes | — |

Constraints:

- `ck_biometric_consents_guardian_required` (CheckConstraint): NOT guardian_required OR guardian_consent_id IS NOT NULL
- `ck_biometric_consents_withdrawal_order` (CheckConstraint): withdrawn_at IS NULL OR withdrawn_at >= granted_at
- `fk_biometric_consents_institution_id_guardian_consent_id_guardian_consents` (ForeignKeyConstraint): institution_id, guardian_consent_id
- `fk_biometric_consents_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_biometric_consents_institution_id_notice_id_consent_notices` (ForeignKeyConstraint): institution_id, notice_id
- `fk_biometric_consents_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_biometric_consents` (PrimaryKeyConstraint): id
- `uq_biometric_consents_tenant_id` (UniqueConstraint): institution_id, id
- `uq_consent_identity` (UniqueConstraint): institution_id, id, user_id

Indexes:

- `ix_biometric_consents_guardian_consent_id` (institution_id, guardian_consent_id)
- `ix_biometric_consents_notice_id` (institution_id, notice_id)
- `ix_biometric_consents_tenant_id` (institution_id)
- `ix_biometric_consents_user_id` (institution_id, user_id)

## biometric_templates

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | no | — |
| consent_id | UUID | no | — |
| model_version_id | UUID | no | — |
| template_version | INTEGER | no | — |
| quality_score | NUMERIC(6, 5) | no | — |
| expires_at | TIMESTAMP WITH TIME ZONE | no | — |
| is_active | BOOLEAN | no | true |
| key_version | VARCHAR(200) | no | — |
| ciphertext | BYTEA | no | — |
| wrapped_key | BYTEA | no | — |
| nonce | BYTEA | no | — |

Constraints:

- `ck_biometric_templates_expiry_order` (CheckConstraint): expires_at > created_at
- `ck_biometric_templates_gcm_nonce_length` (CheckConstraint): octet_length(nonce) = 12
- `ck_biometric_templates_gcm_tag_present` (CheckConstraint): octet_length(ciphertext) >= 16
- `ck_biometric_templates_positive_version` (CheckConstraint): template_version > 0
- `ck_biometric_templates_quality_range` (CheckConstraint): quality_score BETWEEN 0 AND 1
- `ck_biometric_templates_wrapped_key_present` (CheckConstraint): octet_length(wrapped_key) > 0
- `fk_biometric_templates_institution_id_consent_id_biometric_consents` (ForeignKeyConstraint): institution_id, consent_id
- `fk_biometric_templates_institution_id_consent_id_user_id_biometric_consents` (ForeignKeyConstraint): institution_id, consent_id, user_id
- `fk_biometric_templates_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_biometric_templates_institution_id_model_version_id_model_versions` (ForeignKeyConstraint): institution_id, model_version_id
- `fk_biometric_templates_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_biometric_templates` (PrimaryKeyConstraint): id
- `uq_biometric_templates_tenant_id` (UniqueConstraint): institution_id, id
- `uq_template_identity` (UniqueConstraint): institution_id, id, user_id, model_version_id

Indexes:

- `ix_biometric_templates_consent_id` (institution_id, consent_id)
- `ix_biometric_templates_model_version_id` (institution_id, model_version_id)
- `ix_biometric_templates_tenant_id` (institution_id)
- `ix_biometric_templates_user_id` (institution_id, user_id)
- `uq_biometric_templates_active` (institution_id, user_id, model_version_id) UNIQUE WHERE biometric_templates.is_active IS true

## condonation_requests

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| student_id | UUID | no | — |
| semester_id | UUID | no | — |
| reason | TEXT | no | — |
| status | VARCHAR(200) | no | — |
| decided_by_user_id | UUID | yes | — |
| decided_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `ck_condonation_requests_reason_required` (CheckConstraint): length(trim(reason)) > 0
- `ck_condonation_requests_status_values` (CheckConstraint): status IN ('pending', 'approved', 'rejected', 'cancelled')
- `fk_condonation_requests_institution_id_decided_by_user_id_users` (ForeignKeyConstraint): institution_id, decided_by_user_id
- `fk_condonation_requests_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_condonation_requests_institution_id_semester_id_semesters` (ForeignKeyConstraint): institution_id, semester_id
- `fk_condonation_requests_institution_id_student_id_students` (ForeignKeyConstraint): institution_id, student_id
- `pk_condonation_requests` (PrimaryKeyConstraint): id
- `uq_condonation_requests_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_condonation_requests_decided_by_user_id` (institution_id, decided_by_user_id)
- `ix_condonation_requests_semester_id` (institution_id, semester_id)
- `ix_condonation_requests_student_id` (institution_id, student_id)
- `ix_condonation_requests_tenant_id` (institution_id)

## consent_notices

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| version | VARCHAR(200) | no | — |
| purpose | VARCHAR(200) | no | — |
| language | VARCHAR(200) | no | — |
| text | TEXT | no | — |
| retention_days | INTEGER | no | — |

Constraints:

- `ck_consent_notices_positive_retention` (CheckConstraint): retention_days > 0
- `fk_consent_notices_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_consent_notices` (PrimaryKeyConstraint): id
- `uq_consent_notices_institution_id_version_purpose_language` (UniqueConstraint): institution_id, version, purpose, language
- `uq_consent_notices_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_consent_notices_tenant_id` (institution_id)

## courses

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP WITH TIME ZONE | yes | — |
| department_id | UUID | no | — |
| code | VARCHAR(200) | no | — |
| name | VARCHAR(200) | no | — |

Constraints:

- `fk_courses_institution_id_department_id_departments` (ForeignKeyConstraint): institution_id, department_id
- `fk_courses_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_courses` (PrimaryKeyConstraint): id
- `uq_courses_institution_id_code` (UniqueConstraint): institution_id, code
- `uq_courses_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_courses_department_id` (institution_id, department_id)
- `ix_courses_tenant_id` (institution_id)

## data_subject_requests

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | no | — |
| kind | VARCHAR(200) | no | — |
| status | VARCHAR(200) | no | — |
| completed_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `ck_data_subject_requests_kind_values` (CheckConstraint): kind IN ('export', 'delete_biometrics', 'delete_account', 'withdraw_consent')
- `ck_data_subject_requests_status_values` (CheckConstraint): status IN ('pending', 'processing', 'completed', 'rejected')
- `fk_data_subject_requests_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_data_subject_requests_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_data_subject_requests` (PrimaryKeyConstraint): id
- `uq_data_subject_requests_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_data_subject_requests_tenant_id` (institution_id)
- `ix_data_subject_requests_user_id` (institution_id, user_id)

## departments

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP WITH TIME ZONE | yes | — |
| code | VARCHAR(200) | no | — |
| name | VARCHAR(200) | no | — |

Constraints:

- `fk_departments_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_departments` (PrimaryKeyConstraint): id
- `uq_departments_institution_id_code` (UniqueConstraint): institution_id, code
- `uq_departments_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_departments_tenant_id` (institution_id)

## device_bindings

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | no | — |
| device_id | UUID | no | — |
| is_primary | BOOLEAN | no | false |
| approved_at | TIMESTAMP WITH TIME ZONE | yes | — |
| revoked_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `fk_device_bindings_institution_id_device_id_attendance_devices` (ForeignKeyConstraint): institution_id, device_id
- `fk_device_bindings_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_device_bindings_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_device_bindings` (PrimaryKeyConstraint): id
- `uq_device_bindings_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_device_bindings_device_id` (institution_id, device_id)
- `ix_device_bindings_tenant_id` (institution_id)
- `ix_device_bindings_user_id` (institution_id, user_id)
- `uq_device_bindings_primary` (institution_id, user_id) UNIQUE WHERE is_primary AND revoked_at IS NULL

## enrollments

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| student_id | UUID | no | — |
| subject_id | UUID | no | — |
| section_id | UUID | no | — |
| starts_on | DATE | no | — |
| ends_on | DATE | yes | — |

Constraints:

- `ck_enrollments_date_order` (CheckConstraint): ends_on IS NULL OR ends_on >= starts_on
- `fk_enrollments_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_enrollments_institution_id_section_id_sections` (ForeignKeyConstraint): institution_id, section_id
- `fk_enrollments_institution_id_student_id_students` (ForeignKeyConstraint): institution_id, student_id
- `fk_enrollments_institution_id_subject_id_subjects` (ForeignKeyConstraint): institution_id, subject_id
- `pk_enrollments` (PrimaryKeyConstraint): id
- `uq_enrollments_institution_id_student_id_subject_id_section_id_starts_on` (UniqueConstraint): institution_id, student_id, subject_id, section_id, starts_on
- `uq_enrollments_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_enrollments_section_id` (institution_id, section_id)
- `ix_enrollments_student_id` (institution_id, student_id)
- `ix_enrollments_subject_id` (institution_id, subject_id)
- `ix_enrollments_tenant_id` (institution_id)

## events

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| name | VARCHAR(200) | no | — |
| starts_at | TIMESTAMP WITH TIME ZONE | no | — |
| ends_at | TIMESTAMP WITH TIME ZONE | no | — |
| room_id | UUID | yes | — |

Constraints:

- `ck_events_time_order` (CheckConstraint): ends_at > starts_at
- `fk_events_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_events_institution_id_room_id_rooms` (ForeignKeyConstraint): institution_id, room_id
- `pk_events` (PrimaryKeyConstraint): id
- `uq_events_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_events_room_id` (institution_id, room_id)
- `ix_events_tenant_id` (institution_id)

## face_enrollment_sessions

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | no | — |
| consent_id | UUID | no | — |
| status | VARCHAR(200) | no | — |
| challenge | JSONB | no | — |
| expires_at | TIMESTAMP WITH TIME ZONE | no | — |
| accepted_samples | INTEGER | no | 0 |

Constraints:

- `ck_face_enrollment_sessions_expiry_order` (CheckConstraint): expires_at > created_at
- `ck_face_enrollment_sessions_sample_count` (CheckConstraint): accepted_samples BETWEEN 0 AND 8
- `ck_face_enrollment_sessions_status_values` (CheckConstraint): status IN ('pending', 'capturing', 'completed', 'rejected', 'expired')
- `fk_face_enrollment_sessions_institution_id_consent_id_biometric_consents` (ForeignKeyConstraint): institution_id, consent_id
- `fk_face_enrollment_sessions_institution_id_consent_id_user_id_biometric_consents` (ForeignKeyConstraint): institution_id, consent_id, user_id
- `fk_face_enrollment_sessions_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_face_enrollment_sessions_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_face_enrollment_sessions` (PrimaryKeyConstraint): id
- `uq_face_enrollment_sessions_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_face_enrollment_sessions_consent_id` (institution_id, consent_id)
- `ix_face_enrollment_sessions_tenant_id` (institution_id)
- `ix_face_enrollment_sessions_user_id` (institution_id, user_id)

## faculty

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP WITH TIME ZONE | yes | — |
| user_id | UUID | no | — |
| department_id | UUID | no | — |
| employee_number | VARCHAR(200) | no | — |

Constraints:

- `fk_faculty_institution_id_department_id_departments` (ForeignKeyConstraint): institution_id, department_id
- `fk_faculty_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_faculty_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_faculty` (PrimaryKeyConstraint): id
- `uq_faculty_institution_id_employee_number` (UniqueConstraint): institution_id, employee_number
- `uq_faculty_institution_id_user_id` (UniqueConstraint): institution_id, user_id
- `uq_faculty_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_faculty_department_id` (institution_id, department_id)
- `ix_faculty_tenant_id` (institution_id)
- `ix_faculty_user_id` (institution_id, user_id)

## faculty_subjects

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| faculty_id | UUID | no | — |
| subject_id | UUID | no | — |
| section_id | UUID | no | — |

Constraints:

- `fk_faculty_subjects_institution_id_faculty_id_faculty` (ForeignKeyConstraint): institution_id, faculty_id
- `fk_faculty_subjects_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_faculty_subjects_institution_id_section_id_sections` (ForeignKeyConstraint): institution_id, section_id
- `fk_faculty_subjects_institution_id_subject_id_subjects` (ForeignKeyConstraint): institution_id, subject_id
- `pk_faculty_subjects` (PrimaryKeyConstraint): id
- `uq_faculty_subjects_institution_id_faculty_id_subject_id_section_id` (UniqueConstraint): institution_id, faculty_id, subject_id, section_id
- `uq_faculty_subjects_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_faculty_subjects_faculty_id` (institution_id, faculty_id)
- `ix_faculty_subjects_section_id` (institution_id, section_id)
- `ix_faculty_subjects_subject_id` (institution_id, subject_id)
- `ix_faculty_subjects_tenant_id` (institution_id)

## feature_flags

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| key | VARCHAR(200) | no | — |
| enabled | BOOLEAN | no | false |
| configuration | JSONB | no | — |

Constraints:

- `fk_feature_flags_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_feature_flags` (PrimaryKeyConstraint): id
- `uq_feature_flags_institution_id_key` (UniqueConstraint): institution_id, key
- `uq_feature_flags_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_feature_flags_tenant_id` (institution_id)

## guardian_consents

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| parent_link_id | UUID | no | — |
| notice_version | VARCHAR(200) | no | — |
| purpose | VARCHAR(200) | no | — |
| granted_at | TIMESTAMP WITH TIME ZONE | no | — |
| withdrawn_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `fk_guardian_consents_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_guardian_consents_institution_id_parent_link_id_parent_links` (ForeignKeyConstraint): institution_id, parent_link_id
- `pk_guardian_consents` (PrimaryKeyConstraint): id
- `uq_guardian_consents_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_guardian_consents_parent_link_id` (institution_id, parent_link_id)
- `ix_guardian_consents_tenant_id` (institution_id)

## holidays

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| name | VARCHAR(200) | no | — |
| starts_on | DATE | no | — |
| ends_on | DATE | no | — |
| department_id | UUID | yes | — |

Constraints:

- `ck_holidays_date_order` (CheckConstraint): ends_on >= starts_on
- `fk_holidays_institution_id_department_id_departments` (ForeignKeyConstraint): institution_id, department_id
- `fk_holidays_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_holidays` (PrimaryKeyConstraint): id
- `uq_holidays_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_holidays_department_id` (institution_id, department_id)
- `ix_holidays_tenant_id` (institution_id)

## idempotency_keys

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | no | — |
| key_hash | VARCHAR(64) | no | — |
| operation | VARCHAR(200) | no | — |
| request_hash | VARCHAR(64) | no | — |
| response_status | INTEGER | yes | — |
| response | JSONB | yes | — |
| expires_at | TIMESTAMP WITH TIME ZONE | no | — |

Constraints:

- `fk_idempotency_keys_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_idempotency_keys_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_idempotency_keys` (PrimaryKeyConstraint): id
- `uq_idempotency_keys_institution_id_user_id_operation_key_hash` (UniqueConstraint): institution_id, user_id, operation, key_hash
- `uq_idempotency_keys_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_idempotency_keys_tenant_id` (institution_id)
- `ix_idempotency_keys_user_id` (institution_id, user_id)

## import_errors

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| import_job_id | UUID | no | — |
| row_number | INTEGER | no | — |
| field | VARCHAR(200) | no | — |
| code | VARCHAR(200) | no | — |
| message | TEXT | no | — |

Constraints:

- `ck_import_errors_positive_row` (CheckConstraint): row_number > 0
- `fk_import_errors_institution_id_import_job_id_import_jobs` (ForeignKeyConstraint): institution_id, import_job_id
- `fk_import_errors_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_import_errors` (PrimaryKeyConstraint): id
- `uq_import_errors_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_import_errors_import_job_id` (institution_id, import_job_id)
- `ix_import_errors_tenant_id` (institution_id)

## import_jobs

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| requested_by_user_id | UUID | no | — |
| kind | VARCHAR(200) | no | — |
| status | VARCHAR(200) | no | — |
| dry_run | BOOLEAN | no | — |
| file_sha256 | VARCHAR(64) | no | — |
| total_rows | INTEGER | no | 0 |
| error_rows | INTEGER | no | 0 |

Constraints:

- `ck_import_jobs_row_counts` (CheckConstraint): total_rows >= 0 AND error_rows BETWEEN 0 AND total_rows
- `ck_import_jobs_status_values` (CheckConstraint): status IN ('pending', 'validating', 'validated', 'applied', 'failed', 'rolled_back')
- `fk_import_jobs_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_import_jobs_institution_id_requested_by_user_id_users` (ForeignKeyConstraint): institution_id, requested_by_user_id
- `pk_import_jobs` (PrimaryKeyConstraint): id
- `uq_import_jobs_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_import_jobs_requested_by_user_id` (institution_id, requested_by_user_id)
- `ix_import_jobs_tenant_id` (institution_id)

## institutions

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP WITH TIME ZONE | yes | — |
| code | VARCHAR(200) | no | — |
| name | VARCHAR(200) | no | — |
| timezone | VARCHAR(200) | no | — |
| enabled | BOOLEAN | no | true |

Constraints:

- `pk_institutions` (PrimaryKeyConstraint): id
- `uq_institutions_code` (UniqueConstraint): code

Indexes:


## leave_requests

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | no | — |
| kind | VARCHAR(200) | no | — |
| starts_on | DATE | no | — |
| ends_on | DATE | no | — |
| reason | TEXT | no | — |
| status | VARCHAR(200) | no | — |
| evidence_reference | VARCHAR(200) | yes | — |
| decided_by_user_id | UUID | yes | — |
| decided_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `ck_leave_requests_date_order` (CheckConstraint): ends_on >= starts_on
- `ck_leave_requests_kind_values` (CheckConstraint): kind IN ('leave', 'on_duty')
- `ck_leave_requests_reason_required` (CheckConstraint): length(trim(reason)) > 0
- `ck_leave_requests_status_values` (CheckConstraint): status IN ('pending', 'approved', 'rejected', 'cancelled')
- `fk_leave_requests_institution_id_decided_by_user_id_users` (ForeignKeyConstraint): institution_id, decided_by_user_id
- `fk_leave_requests_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_leave_requests_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_leave_requests` (PrimaryKeyConstraint): id
- `uq_leave_requests_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_leave_requests_decided_by_user_id` (institution_id, decided_by_user_id)
- `ix_leave_requests_tenant_id` (institution_id)
- `ix_leave_requests_user_id` (institution_id, user_id)

## liveness_events

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| verification_attempt_id | UUID | yes | — |
| enrollment_session_id | UUID | yes | — |
| challenge_type | VARCHAR(200) | no | — |
| passed | BOOLEAN | no | — |
| reason_codes | JSONB | no | — |

Constraints:

- `ck_liveness_events_one_parent` (CheckConstraint): num_nonnulls(verification_attempt_id, enrollment_session_id) = 1
- `fk_liveness_events_institution_id_enrollment_session_id_face_enrollment_sessions` (ForeignKeyConstraint): institution_id, enrollment_session_id
- `fk_liveness_events_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_liveness_events_institution_id_verification_attempt_id_verification_attempts` (ForeignKeyConstraint): institution_id, verification_attempt_id
- `pk_liveness_events` (PrimaryKeyConstraint): id
- `uq_liveness_events_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_liveness_events_enrollment_session_id` (institution_id, enrollment_session_id)
- `ix_liveness_events_tenant_id` (institution_id)
- `ix_liveness_events_verification_attempt_id` (institution_id, verification_attempt_id)

## model_versions

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| name | VARCHAR(200) | no | — |
| version | VARCHAR(200) | no | — |
| checksum_sha256 | VARCHAR(64) | no | — |
| license | TEXT | no | — |
| artifact_reference | VARCHAR(200) | no | — |
| evaluation_metrics | JSONB | no | — |
| rollout_status | VARCHAR(200) | no | — |

Constraints:

- `ck_model_versions_rollout_status_values` (CheckConstraint): rollout_status IN ('candidate', 'shadow', 'active', 'retired', 'blocked')
- `ck_model_versions_valid_checksum` (CheckConstraint): checksum_sha256 ~ '^[0-9a-f]{64}$'
- `fk_model_versions_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_model_versions` (PrimaryKeyConstraint): id
- `uq_model_versions_institution_id_name_version` (UniqueConstraint): institution_id, name, version
- `uq_model_versions_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_model_versions_tenant_id` (institution_id)

## notifications

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | no | — |
| kind | VARCHAR(200) | no | — |
| content | JSONB | no | — |
| read_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `fk_notifications_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_notifications_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_notifications` (PrimaryKeyConstraint): id
- `uq_notifications_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_notifications_tenant_id` (institution_id)
- `ix_notifications_user_id` (institution_id, user_id)

## outbox_events

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| event_type | VARCHAR(200) | no | — |
| aggregate_id | UUID | no | — |
| payload | JSONB | no | — |
| available_at | TIMESTAMP WITH TIME ZONE | no | — |
| published_at | TIMESTAMP WITH TIME ZONE | yes | — |
| attempts | INTEGER | no | 0 |

Constraints:

- `ck_outbox_events_nonnegative_attempts` (CheckConstraint): attempts >= 0
- `fk_outbox_events_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_outbox_events` (PrimaryKeyConstraint): id
- `uq_outbox_events_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_outbox_events_aggregate_id` (institution_id, aggregate_id)
- `ix_outbox_events_tenant_id` (institution_id)
- `ix_outbox_pending` (available_at, institution_id) WHERE outbox_events.published_at IS NULL

## parent_links

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| parent_user_id | UUID | no | — |
| student_id | UUID | no | — |
| relationship | VARCHAR(200) | no | — |
| consented_at | TIMESTAMP WITH TIME ZONE | yes | — |
| revoked_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `fk_parent_links_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_parent_links_institution_id_parent_user_id_users` (ForeignKeyConstraint): institution_id, parent_user_id
- `fk_parent_links_institution_id_student_id_students` (ForeignKeyConstraint): institution_id, student_id
- `pk_parent_links` (PrimaryKeyConstraint): id
- `uq_parent_links_institution_id_parent_user_id_student_id` (UniqueConstraint): institution_id, parent_user_id, student_id
- `uq_parent_links_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_parent_links_parent_user_id` (institution_id, parent_user_id)
- `ix_parent_links_student_id` (institution_id, student_id)
- `ix_parent_links_tenant_id` (institution_id)

## permissions

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| code | VARCHAR(200) | no | — |
| description | TEXT | no | — |

Constraints:

- `pk_permissions` (PrimaryKeyConstraint): id
- `uq_permissions_code` (UniqueConstraint): code

Indexes:


## refresh_tokens

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | no | — |
| family_id | UUID | no | — |
| token_hash | VARCHAR(64) | no | — |
| expires_at | TIMESTAMP WITH TIME ZONE | no | — |
| used_at | TIMESTAMP WITH TIME ZONE | yes | — |
| revoked_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `ck_refresh_tokens_expiry_order` (CheckConstraint): expires_at > created_at
- `fk_refresh_tokens_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_refresh_tokens_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_refresh_tokens` (PrimaryKeyConstraint): id
- `uq_refresh_tokens_institution_id_token_hash` (UniqueConstraint): institution_id, token_hash
- `uq_refresh_tokens_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_refresh_tokens_family_id` (institution_id, family_id)
- `ix_refresh_tokens_tenant_id` (institution_id)
- `ix_refresh_tokens_user_id` (institution_id, user_id)

## report_jobs

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| requested_by_user_id | UUID | no | — |
| kind | VARCHAR(200) | no | — |
| format | VARCHAR(200) | no | — |
| status | VARCHAR(200) | no | — |
| filters | JSONB | no | — |
| object_reference | VARCHAR(200) | yes | — |
| expires_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `ck_report_jobs_format_values` (CheckConstraint): format IN ('csv', 'xlsx', 'pdf')
- `ck_report_jobs_status_values` (CheckConstraint): status IN ('pending', 'processing', 'completed', 'failed', 'expired')
- `fk_report_jobs_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_report_jobs_institution_id_requested_by_user_id_users` (ForeignKeyConstraint): institution_id, requested_by_user_id
- `pk_report_jobs` (PrimaryKeyConstraint): id
- `uq_report_jobs_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_report_jobs_requested_by_user_id` (institution_id, requested_by_user_id)
- `ix_report_jobs_tenant_id` (institution_id)

## retention_policies

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| data_category | VARCHAR(200) | no | — |
| retention_days | INTEGER | no | — |
| trigger | VARCHAR(200) | no | — |

Constraints:

- `ck_retention_policies_positive_retention` (CheckConstraint): retention_days > 0
- `fk_retention_policies_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_retention_policies` (PrimaryKeyConstraint): id
- `uq_retention_policies_institution_id_data_category` (UniqueConstraint): institution_id, data_category
- `uq_retention_policies_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_retention_policies_tenant_id` (institution_id)

## role_permissions

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| role_id | UUID | no | — |
| permission_id | UUID | no | — |

Constraints:

- `fk_role_permissions_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_role_permissions_institution_id_role_id_roles` (ForeignKeyConstraint): institution_id, role_id
- `fk_role_permissions_permission_id_permissions` (ForeignKeyConstraint): permission_id
- `pk_role_permissions` (PrimaryKeyConstraint): id
- `uq_role_permissions_institution_id_role_id_permission_id` (UniqueConstraint): institution_id, role_id, permission_id
- `uq_role_permissions_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_role_permissions_permission_id` (institution_id, permission_id)
- `ix_role_permissions_role_id` (institution_id, role_id)
- `ix_role_permissions_tenant_id` (institution_id)

## roles

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| code | VARCHAR(200) | no | — |
| name | VARCHAR(200) | no | — |

Constraints:

- `fk_roles_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_roles` (PrimaryKeyConstraint): id
- `uq_roles_institution_id_code` (UniqueConstraint): institution_id, code
- `uq_roles_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_roles_tenant_id` (institution_id)

## rooms

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP WITH TIME ZONE | yes | — |
| code | VARCHAR(200) | no | — |
| name | VARCHAR(200) | no | — |
| capacity | INTEGER | no | — |
| department_id | UUID | yes | — |

Constraints:

- `ck_rooms_positive_capacity` (CheckConstraint): capacity > 0
- `fk_rooms_institution_id_department_id_departments` (ForeignKeyConstraint): institution_id, department_id
- `fk_rooms_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_rooms` (PrimaryKeyConstraint): id
- `uq_rooms_institution_id_code` (UniqueConstraint): institution_id, code
- `uq_rooms_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_rooms_department_id` (institution_id, department_id)
- `ix_rooms_tenant_id` (institution_id)

## sections

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP WITH TIME ZONE | yes | — |
| semester_id | UUID | no | — |
| code | VARCHAR(200) | no | — |
| name | VARCHAR(200) | no | — |

Constraints:

- `fk_sections_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_sections_institution_id_semester_id_semesters` (ForeignKeyConstraint): institution_id, semester_id
- `pk_sections` (PrimaryKeyConstraint): id
- `uq_sections_institution_id_semester_id_code` (UniqueConstraint): institution_id, semester_id, code
- `uq_sections_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_sections_semester_id` (institution_id, semester_id)
- `ix_sections_tenant_id` (institution_id)

## semesters

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| course_id | UUID | no | — |
| academic_year_id | UUID | no | — |
| number | INTEGER | no | — |
| starts_on | DATE | no | — |
| ends_on | DATE | no | — |

Constraints:

- `ck_semesters_date_order` (CheckConstraint): ends_on >= starts_on
- `ck_semesters_positive_number` (CheckConstraint): number > 0
- `fk_semesters_institution_id_academic_year_id_academic_years` (ForeignKeyConstraint): institution_id, academic_year_id
- `fk_semesters_institution_id_course_id_courses` (ForeignKeyConstraint): institution_id, course_id
- `fk_semesters_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_semesters` (PrimaryKeyConstraint): id
- `uq_semesters_institution_id_course_id_academic_year_id_number` (UniqueConstraint): institution_id, course_id, academic_year_id, number
- `uq_semesters_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_semesters_academic_year_id` (institution_id, academic_year_id)
- `ix_semesters_course_id` (institution_id, course_id)
- `ix_semesters_tenant_id` (institution_id)

## session_qr_tokens

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| session_id | UUID | no | — |
| token_hash | VARCHAR(64) | no | — |
| valid_from | TIMESTAMP WITH TIME ZONE | no | — |
| expires_at | TIMESTAMP WITH TIME ZONE | no | — |

Constraints:

- `ck_session_qr_tokens_validity_order` (CheckConstraint): expires_at > valid_from
- `fk_session_qr_tokens_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_session_qr_tokens_institution_id_session_id_attendance_sessions` (ForeignKeyConstraint): institution_id, session_id
- `pk_session_qr_tokens` (PrimaryKeyConstraint): id
- `uq_session_qr_tokens_institution_id_token_hash` (UniqueConstraint): institution_id, token_hash
- `uq_session_qr_tokens_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_session_qr_tokens_session_id` (institution_id, session_id)
- `ix_session_qr_tokens_tenant_id` (institution_id)

## staff

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP WITH TIME ZONE | yes | — |
| user_id | UUID | no | — |
| department_id | UUID | yes | — |
| employee_number | VARCHAR(200) | no | — |

Constraints:

- `fk_staff_institution_id_department_id_departments` (ForeignKeyConstraint): institution_id, department_id
- `fk_staff_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_staff_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_staff` (PrimaryKeyConstraint): id
- `uq_staff_institution_id_employee_number` (UniqueConstraint): institution_id, employee_number
- `uq_staff_institution_id_user_id` (UniqueConstraint): institution_id, user_id
- `uq_staff_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_staff_department_id` (institution_id, department_id)
- `ix_staff_tenant_id` (institution_id)
- `ix_staff_user_id` (institution_id, user_id)

## students

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP WITH TIME ZONE | yes | — |
| user_id | UUID | no | — |
| department_id | UUID | no | — |
| section_id | UUID | no | — |
| registration_number | VARCHAR(200) | no | — |
| graduation_date | DATE | yes | — |

Constraints:

- `fk_students_institution_id_department_id_departments` (ForeignKeyConstraint): institution_id, department_id
- `fk_students_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_students_institution_id_section_id_sections` (ForeignKeyConstraint): institution_id, section_id
- `fk_students_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_students` (PrimaryKeyConstraint): id
- `uq_students_institution_id_registration_number` (UniqueConstraint): institution_id, registration_number
- `uq_students_institution_id_user_id` (UniqueConstraint): institution_id, user_id
- `uq_students_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_students_department_id` (institution_id, department_id)
- `ix_students_section_id` (institution_id, section_id)
- `ix_students_tenant_id` (institution_id)
- `ix_students_user_id` (institution_id, user_id)

## subjects

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP WITH TIME ZONE | yes | — |
| department_id | UUID | no | — |
| code | VARCHAR(200) | no | — |
| name | VARCHAR(200) | no | — |

Constraints:

- `fk_subjects_institution_id_department_id_departments` (ForeignKeyConstraint): institution_id, department_id
- `fk_subjects_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_subjects` (PrimaryKeyConstraint): id
- `uq_subjects_institution_id_code` (UniqueConstraint): institution_id, code
- `uq_subjects_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_subjects_department_id` (institution_id, department_id)
- `ix_subjects_tenant_id` (institution_id)

## system_settings

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| key | VARCHAR(200) | no | — |
| value | JSONB | no | — |

Constraints:

- `fk_system_settings_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_system_settings` (PrimaryKeyConstraint): id
- `uq_system_settings_institution_id_key` (UniqueConstraint): institution_id, key
- `uq_system_settings_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_system_settings_tenant_id` (institution_id)

## timetable_entries

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| academic_year_id | UUID | no | — |
| section_id | UUID | no | — |
| subject_id | UUID | no | — |
| faculty_id | UUID | no | — |
| room_id | UUID | no | — |
| weekday | INTEGER | no | — |
| starts_at | TIME WITHOUT TIME ZONE | no | — |
| ends_at | TIME WITHOUT TIME ZONE | no | — |
| valid_from | DATE | no | — |
| valid_until | DATE | no | — |

Constraints:

- `ck_timetable_entries_date_order` (CheckConstraint): valid_until >= valid_from
- `ck_timetable_entries_time_order` (CheckConstraint): ends_at > starts_at
- `ck_timetable_entries_weekday_range` (CheckConstraint): weekday BETWEEN 0 AND 6
- `fk_timetable_entries_institution_id_academic_year_id_academic_years` (ForeignKeyConstraint): institution_id, academic_year_id
- `fk_timetable_entries_institution_id_faculty_id_faculty` (ForeignKeyConstraint): institution_id, faculty_id
- `fk_timetable_entries_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_timetable_entries_institution_id_room_id_rooms` (ForeignKeyConstraint): institution_id, room_id
- `fk_timetable_entries_institution_id_section_id_sections` (ForeignKeyConstraint): institution_id, section_id
- `fk_timetable_entries_institution_id_subject_id_subjects` (ForeignKeyConstraint): institution_id, subject_id
- `pk_timetable_entries` (PrimaryKeyConstraint): id
- `uq_timetable_entries_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_timetable_entries_academic_year_id` (institution_id, academic_year_id)
- `ix_timetable_entries_faculty_id` (institution_id, faculty_id)
- `ix_timetable_entries_room_id` (institution_id, room_id)
- `ix_timetable_entries_section_id` (institution_id, section_id)
- `ix_timetable_entries_subject_id` (institution_id, subject_id)
- `ix_timetable_entries_tenant_id` (institution_id)

## user_roles

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | no | — |
| role_id | UUID | no | — |
| department_id | UUID | yes | — |
| section_id | UUID | yes | — |

Constraints:

- `ck_user_roles_scope_hierarchy` (CheckConstraint): section_id IS NULL OR department_id IS NOT NULL
- `fk_user_roles_institution_id_department_id_departments` (ForeignKeyConstraint): institution_id, department_id
- `fk_user_roles_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_user_roles_institution_id_role_id_roles` (ForeignKeyConstraint): institution_id, role_id
- `fk_user_roles_institution_id_section_id_sections` (ForeignKeyConstraint): institution_id, section_id
- `fk_user_roles_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_user_roles` (PrimaryKeyConstraint): id
- `uq_user_roles_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_user_roles_department_id` (institution_id, department_id)
- `ix_user_roles_role_id` (institution_id, role_id)
- `ix_user_roles_section_id` (institution_id, section_id)
- `ix_user_roles_tenant_id` (institution_id)
- `ix_user_roles_user_id` (institution_id, user_id)
- `uq_user_roles_scope` (institution_id, user_id, role_id, department_id, section_id) UNIQUE

## users

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| deleted_at | TIMESTAMP WITH TIME ZONE | yes | — |
| email | VARCHAR(320) | no | — |
| display_name | VARCHAR(200) | no | — |
| password_hash | TEXT | yes | — |
| is_active | BOOLEAN | no | true |
| mfa_required | BOOLEAN | no | false |
| mfa_secret_ciphertext | BYTEA | yes | — |
| external_subject | VARCHAR(200) | yes | — |

Constraints:

- `ck_users_email_normalized` (CheckConstraint): email = lower(email) AND position('@' in email) > 1
- `fk_users_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_users` (PrimaryKeyConstraint): id
- `uq_users_institution_id_email` (UniqueConstraint): institution_id, email
- `uq_users_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_users_tenant_id` (institution_id)

## verification_attempts

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| user_id | UUID | no | — |
| session_id | UUID | no | — |
| model_version_id | UUID | no | — |
| template_id | UUID | yes | — |
| device_id | UUID | yes | — |
| outcome | VARCHAR(200) | no | — |
| similarity_score | NUMERIC(8, 6) | yes | — |
| confidence | NUMERIC(6, 5) | yes | — |
| reason_codes | JSONB | no | — |
| threshold_snapshot | JSONB | no | — |
| challenge_passed | BOOLEAN | no | — |
| verified_at | TIMESTAMP WITH TIME ZONE | yes | — |

Constraints:

- `ck_verification_attempts_confidence_range` (CheckConstraint): confidence IS NULL OR confidence BETWEEN 0 AND 1
- `ck_verification_attempts_outcome_values` (CheckConstraint): outcome IN ('verified', 'rejected', 'manual_review')
- `ck_verification_attempts_verified_evidence` (CheckConstraint): outcome <> 'verified' OR (challenge_passed AND verified_at IS NOT NULL AND template_id IS NOT NULL)
- `fk_verification_attempts_institution_id_device_id_attendance_devices` (ForeignKeyConstraint): institution_id, device_id
- `fk_verification_attempts_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_verification_attempts_institution_id_model_version_id_model_versions` (ForeignKeyConstraint): institution_id, model_version_id
- `fk_verification_attempts_institution_id_session_id_attendance_sessions` (ForeignKeyConstraint): institution_id, session_id
- `fk_verification_attempts_institution_id_template_id_biometric_templates` (ForeignKeyConstraint): institution_id, template_id
- `fk_verification_attempts_institution_id_template_id_user_id_model_version_id_biometric_templates` (ForeignKeyConstraint): institution_id, template_id, user_id, model_version_id
- `fk_verification_attempts_institution_id_user_id_users` (ForeignKeyConstraint): institution_id, user_id
- `pk_verification_attempts` (PrimaryKeyConstraint): id
- `uq_verification_attempts_tenant_id` (UniqueConstraint): institution_id, id
- `uq_verification_identity` (UniqueConstraint): institution_id, id, user_id, session_id, outcome

Indexes:

- `ix_verification_attempts_device_id` (institution_id, device_id)
- `ix_verification_attempts_model_version_id` (institution_id, model_version_id)
- `ix_verification_attempts_session_id` (institution_id, session_id)
- `ix_verification_attempts_template_id` (institution_id, template_id)
- `ix_verification_attempts_tenant_id` (institution_id)
- `ix_verification_attempts_user_id` (institution_id, user_id)

## webhook_deliveries

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| webhook_id | UUID | no | — |
| outbox_event_id | UUID | no | — |
| status | VARCHAR(200) | no | — |
| attempts | INTEGER | no | 0 |
| next_attempt_at | TIMESTAMP WITH TIME ZONE | no | — |
| last_http_status | INTEGER | yes | — |

Constraints:

- `ck_webhook_deliveries_nonnegative_attempts` (CheckConstraint): attempts >= 0
- `ck_webhook_deliveries_status_values` (CheckConstraint): status IN ('pending', 'delivered', 'failed')
- `fk_webhook_deliveries_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `fk_webhook_deliveries_institution_id_outbox_event_id_outbox_events` (ForeignKeyConstraint): institution_id, outbox_event_id
- `fk_webhook_deliveries_institution_id_webhook_id_webhooks` (ForeignKeyConstraint): institution_id, webhook_id
- `pk_webhook_deliveries` (PrimaryKeyConstraint): id
- `uq_webhook_deliveries_institution_id_webhook_id_outbox_event_id` (UniqueConstraint): institution_id, webhook_id, outbox_event_id
- `uq_webhook_deliveries_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_webhook_deliveries_outbox_event_id` (institution_id, outbox_event_id)
- `ix_webhook_deliveries_tenant_id` (institution_id)
- `ix_webhook_deliveries_webhook_id` (institution_id, webhook_id)

## webhooks

| Column | PostgreSQL type | Nullable | Default |
| --- | --- | --- | --- |
| id | UUID | no | gen_random_uuid() |
| institution_id | UUID | no | — |
| created_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP WITH TIME ZONE | no | CURRENT_TIMESTAMP |
| created_by_user_id | UUID | no | — |
| url | TEXT | no | — |
| signing_secret_ciphertext | BYTEA | no | — |
| event_types | JSONB | no | — |
| enabled | BOOLEAN | no | false |

Constraints:

- `ck_webhooks_https_required` (CheckConstraint): url LIKE 'https://%'
- `fk_webhooks_institution_id_created_by_user_id_users` (ForeignKeyConstraint): institution_id, created_by_user_id
- `fk_webhooks_institution_id_institutions` (ForeignKeyConstraint): institution_id
- `pk_webhooks` (PrimaryKeyConstraint): id
- `uq_webhooks_tenant_id` (UniqueConstraint): institution_id, id

Indexes:

- `ix_webhooks_created_by_user_id` (institution_id, created_by_user_id)
- `ix_webhooks_tenant_id` (institution_id)
