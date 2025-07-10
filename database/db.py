import sqlite3

DB_PATH = "jobs.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            description TEXT,
            requirements TEXT,
            optionals TEXT,
            salary TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            job_id INTEGER,
            phone TEXT,  
            skills TEXT,
            match_score INTEGER,
            FOREIGN KEY (job_id) REFERENCES jobs (id)
        )
    ''')

    for column in ["description", "salary", "requirements"]:
        try:
            cursor.execute(f"ALTER TABLE jobs ADD COLUMN {column} TEXT")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

get_connection()
init_db()