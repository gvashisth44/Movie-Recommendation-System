import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS last_search (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        movie TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()
