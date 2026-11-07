-- Local development only. Cluster roles are infrastructure; schemas are Alembic-only.
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aifams_app') THEN
        CREATE ROLE aifams_app NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aifams_biometric') THEN
        CREATE ROLE aifams_biometric NOLOGIN NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aifams_runtime') THEN
        CREATE ROLE aifams_runtime LOGIN PASSWORD 'aifams_runtime_local'
            NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'aifams_runtime'
               AND (rolsuper OR rolbypassrls OR rolcreaterole OR rolcreatedb)) THEN
        RAISE EXCEPTION 'Unsafe runtime role attributes';
    END IF;
END $$;
GRANT aifams_app TO aifams_runtime;
