import sqlite3

def get_last_search():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT movie FROM last_search ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def set_last_search(movie):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO last_search (movie) VALUES (?)', (movie,))
    conn.commit()
    conn.close()
