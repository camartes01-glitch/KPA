-- KPA Welfare Management System — Database Initialization Script
-- This script runs once when the Docker container first starts.
-- Alembic manages the actual schema; this just ensures extensions are ready.

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Enable pg_trgm for full-text search performance
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
-- Enable btree_gin for composite indexes
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Set timezone
SET timezone = 'Asia/Kolkata';
