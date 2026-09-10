#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '${DB_APP_USER}') THEN
        CREATE ROLE ${DB_APP_USER} WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT PASSWORD '${DB_APP_PASSWORD}';
    END IF;
END
\$\$;

GRANT CONNECT ON DATABASE ${DB_NAME} TO ${DB_APP_USER};
GRANT USAGE ON SCHEMA public TO ${DB_APP_USER};

-- Explicitly revoke CREATE so this user cannot run migrations or alter schema
REVOKE CREATE ON SCHEMA public FROM ${DB_APP_USER};

-- 1. Grant on all CURRENT tables (in case any exist before migrations)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ${DB_APP_USER};

-- 2. Grant on all CURRENT sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ${DB_APP_USER};

-- 3. CRITICAL FIX: Default privileges for tables created by the POSTGRES_USER (DB_ADMIN_USER)
-- This ensures that when 'manage.py migrate' creates auth_user, django_session, etc., 
-- DB_APP_USER automatically inherits the correct permissions.
ALTER DEFAULT PRIVILEGES FOR ROLE "$POSTGRES_USER" IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${DB_APP_USER};
ALTER DEFAULT PRIVILEGES FOR ROLE "$POSTGRES_USER" IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO ${DB_APP_USER};

EOSQL
