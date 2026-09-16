import psycopg2

conn = psycopg2.connect(
    dbname="kpa_staging",
    user="kpa_user",
    password="kpa_staging_pwd",
    host="172.29.27.245",
    port=5432
)
cur = conn.cursor()

print("--- PRIMARY KEYS ---")
cur.execute("""
    SELECT tc.table_name, ccu.column_name 
    FROM information_schema.table_constraints tc 
    JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name 
    WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_schema = 'public'
    ORDER BY tc.table_name;
""")
for r in cur.fetchall():
    print(f"PK: {r[0]}.{r[1]}")

print("\n--- FOREIGN KEYS ---")
cur.execute("""
    SELECT tc.table_name, kcu.column_name, ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name 
    FROM information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name 
    JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name 
    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema='public'
    ORDER BY tc.table_name;
""")
for r in cur.fetchall():
    print(f"FK: {r[0]}.{r[1]} -> {r[2]}.{r[3]}")

print("\n--- UNIQUE CONSTRAINTS ---")
cur.execute("""
    SELECT tc.table_name, kcu.column_name, tc.constraint_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
    WHERE tc.constraint_type = 'UNIQUE' AND tc.table_schema = 'public'
    ORDER BY tc.table_name;
""")
for r in cur.fetchall():
    print(f"UNIQUE: {r[0]}.{r[1]} ({r[2]})")

print("\n--- INDEXES ---")
cur.execute("""
    SELECT tablename, indexname 
    FROM pg_indexes 
    WHERE schemaname = 'public'
    ORDER BY tablename, indexname;
""")
indexes = cur.fetchall()
print(f"Total Indexes: {len(indexes)}")
for r in indexes[:15]:
    print(f"INDEX: {r[0]}.{r[1]}")
if len(indexes) > 15:
    print(f"... and {len(indexes) - 15} more indexes")

print("\n--- ENUMS (Checking for duplicate PostgreSQL enum types) ---")
cur.execute("SELECT typname FROM pg_type WHERE typtype = 'e';")
enums = cur.fetchall()
print(f"PostgreSQL Enums: {enums}")

conn.close()
