import sqlite3

conn = sqlite3.connect("food_ai.db", check_same_thread=False)
c = conn.cursor()

def create_tables():

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS donations(
        food TEXT,
        quantity INTEGER,
        expiry INTEGER
    )
    """)

    conn.commit()