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


def add_candidate(name, job_id, phone, skills):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Преобразуем словарь навыков в строку
        skills_str = ", ".join([f"{skill}: {'+' if has else '-'}"
                                for skill, has in skills.items()])

        cursor.execute('''
            INSERT INTO candidates (name, job_id, phone, skills, match_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, job_id, phone, skills_str, 0))

        conn.commit()  # Важно: подтверждаем изменения
        return True
    except Exception as e:
        print(f"Ошибка при добавлении кандидата: {e}")
        conn.rollback()
        return False
    finally:
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
    return cursor.fetchall()

def get_job_skills(job_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT requirements FROM jobs WHERE id=?", (job_id,))
        result = cursor.fetchone()
        if result and result[0]:
            return result[0].split(',')  # Предполагаем, что навыки хранятся через запятую
        return []
    finally:
        conn.close()