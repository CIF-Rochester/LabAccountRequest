import sqlite3
from config import config

conn = sqlite3.connect(config.db.db_file)

with open('schema.sql') as f:
    conn.executescript(f.read())
