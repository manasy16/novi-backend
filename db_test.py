from sqlalchemy import text

from app.db.database import engine


def test_connection():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))

        print("Connected successfully!")
        print(result.fetchone())


if __name__ == "__main__":
    test_connection()