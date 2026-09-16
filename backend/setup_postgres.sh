su - postgres << 'EOF'
psql -tc "SELECT 1 FROM pg_roles WHERE rolname='kpa_user'" | grep -q 1 || psql -c "CREATE USER kpa_user WITH PASSWORD 'kpa_staging_pwd' CREATEDB;"
psql -tc "SELECT 1 FROM pg_database WHERE datname='kpa_staging'" | grep -q 1 || psql -c "CREATE DATABASE kpa_staging OWNER kpa_user;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE kpa_staging TO kpa_user;"
psql -d kpa_staging -c "GRANT ALL ON SCHEMA public TO kpa_user;"
psql -d kpa_staging -c "SELECT current_database(), current_user;"
EOF
