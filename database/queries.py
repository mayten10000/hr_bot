from .db import get_connection

def get_all_jobs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM jobs")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def get_job_details(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, salary, requirements FROM jobs WHERE id=?", (job_id,))
    job = cursor.fetchone()
    conn.close()
    return job

def add_candidate(name, job_id, skills_text, score):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO candidates (name, job_id, skills, match_score) VALUES (?, ?, ?, ?)",
                   (name, job_id, skills_text, score))
    conn.commit()
    conn.close()

def delete_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()


def get_all_candidates():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, job_id, skills, match_score FROM candidates ORDER BY match_score DESC")
    conn.commit()
    conn.close()
