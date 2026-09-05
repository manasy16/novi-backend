from sqlalchemy import inspect

from app.db.database import engine


def check_tables():
    inspector = inspect(engine)

    tables = inspector.get_table_names()

    print("\nTables in database:\n")

    for table in sorted(tables):
        print(f"✓ {table}")


if __name__ == "__main__":
    check_tables()