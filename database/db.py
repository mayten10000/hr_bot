import sqlite3

DB_PATH = "jobs.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            full_name TEXT,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')



    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            title TEXT,
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

    for column in ["category", "title", "description", "requirements", "optionals", "salary"]:
        try:
            cursor.execute(f"ALTER TABLE jobs ADD COLUMN {column} TEXT")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

'''
get_connection()
init_db()
'''