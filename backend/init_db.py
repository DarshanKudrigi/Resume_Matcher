import asyncio
import os
import sys
import urllib.parse
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.database import Base
import app.models  # load all models

async def init_postgres():
    print("=" * 60)
    print("ResumeMate - PostgreSQL Database Setup")
    print("=" * 60)
    print(f"Host:     {settings.DB_HOST}")
    print(f"Port:     {settings.DB_PORT}")
    print(f"User:     {settings.DB_USER}")
    print(f"Database: {settings.DB_NAME}")
    print("-" * 60)

    # 1. Connect to postgres maintenance DB to check/create target database
    # URL-encode password to handle special characters like @ ! # etc.
    encoded_password = urllib.parse.quote_plus(settings.DB_PASSWORD)
    maintenance_url = f"postgresql+asyncpg://{settings.DB_USER}:{encoded_password}@{settings.DB_HOST}:{settings.DB_PORT}/postgres"
    print(f"Checking if database '{settings.DB_NAME}' exists...")
    try:
        m_engine = create_async_engine(maintenance_url, isolation_level="AUTOCOMMIT")
        async with m_engine.connect() as conn:
            check_sql = text(f"SELECT 1 FROM pg_database WHERE datname = '{settings.DB_NAME}'")
            res = await conn.execute(check_sql)
            if not res.scalar():
                print(f"Database '{settings.DB_NAME}' not found. Creating...")
                await conn.execute(text(f"CREATE DATABASE {settings.DB_NAME}"))
                print(f"Database '{settings.DB_NAME}' created successfully!")
            else:
                print(f"Database '{settings.DB_NAME}' already exists.")
        await m_engine.dispose()
    except Exception as e:
        print(f"[!] Warning: Could not connect to default maintenance database: {e}")
        print("    If you haven't set your PostgreSQL password, please update DB_PASSWORD in backend/.env")
        print("    Continuing with direct connection attempt...")

    # 2. Connect to the application database and create tables
    app_db_url = settings.get_database_url()
    print(f"\nConnecting to target database '{settings.DB_NAME}'...")
    try:
        app_engine = create_async_engine(app_db_url, echo=False)
        async with app_engine.begin() as conn:
            print("Creating all database tables (users, resumes, job_postings, analysis_history, etc.)...")
            await conn.run_sync(Base.metadata.create_all)
        print("All tables created successfully in PostgreSQL!")
        await app_engine.dispose()
        print("\nSetup complete! You can now start the server with: python run.py")
    except Exception as e:
        print(f"\n[X] Error creating tables in PostgreSQL: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check DB_PASSWORD in backend/.env")
        print("2. Ensure PostgreSQL service is running ('Get-Service *postgres*' in PowerShell)")
        print("3. Alternatively, run the app with FALLBACK_TO_SQLITE=True to test immediately.")

if __name__ == "__main__":
    asyncio.run(init_postgres())
