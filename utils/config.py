from db import sqlite

CONNECTION_STRING = "test_db"
DB_TYPE = "sqlite"

databases = {"sqlite": sqlite.Sqlite}
