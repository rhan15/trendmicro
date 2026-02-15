from app.packages import os, Path
import psycopg2

def getPostgresConnection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=int(os.getenv("POSTGRES_PORT")),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB")
        )
        return conn
    except Exception as e:
        print("PostgreSQL Connection Error:", e)
        return None