import sqlite3
import json

def init_db():
    conn = sqlite3.connect('tetris_solver.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS max_attempts
                 (params TEXT PRIMARY KEY, max_attempts INTEGER)''')
    conn.commit()
    conn.close()

def get_cached_max_attempts(params):
    conn = sqlite3.connect('tetris_solver.db')
    c = conn.cursor()
    c.execute("SELECT max_attempts FROM max_attempts WHERE params = ?", (json.dumps(params),))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def cache_max_attempts(params, max_attempts):
    conn = sqlite3.connect('tetris_solver.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO max_attempts (params, max_attempts) VALUES (?, ?)",
              (json.dumps(params), max_attempts))
    conn.commit()
    conn.close()
