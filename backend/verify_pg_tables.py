import os
import psycopg2

conn = psycopg2.connect(
    dbname="kpa_staging",
    user="kpa_user",
    password="kpa_staging_pwd",
    host="172.29.27.245",
    port=5432
)
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;")
tables = [row[0] for row in cur.fetchall()]
print(f"PostgreSQL Tables ({len(tables)}):", tables)

cur.execute("SELECT version_num FROM alembic_version;")
print("Alembic current version:", cur.fetchall())
conn.close()
