import os
from dotenv import load_dotenv

from db import sqlite
from db import postgres

load_dotenv()

def get_pg_conn_str():
    return f"""
    dbname={os.getenv('POSTGRES_DB')}
    user={os.getenv('POSTGRES_USER')}
    password={os.getenv('POSTGRES_PASSWORD')}
    host={os.getenv('POSTGRES_HOST')}
    port={os.getenv('POSTGRES_PORT')}
    """

DB_TYPE = os.getenv("DB_TYPE", "sqlite")

databases = {
    "sqlite": {"module": sqlite.Sqlite, "connection_string": os.getenv('SQLITE_DB')},
    "postgres": {"module": postgres.Postgres, "connection_string": get_pg_conn_str()}
}

