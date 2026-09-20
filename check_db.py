from sqlalchemy import text
from app.db.database import engine

with engine.connect() as connection:
    rows = connection.execute(
        text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
    ).all()

print("ALL DATABASE TABLES:")
for row in rows:
    print("-", row[0])