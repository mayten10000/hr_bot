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
    cursor.execute("SELECT category, title, description, salary, requirements, optionals FROM jobs WHERE id=?", (job_id,))
    job = cursor.fetchone()
    conn.close()
    return job

def get_category_jobs(job_category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM jobs WHERE category=?", (job_category,))
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def add_candidate(name, job_id, phone, skills, match_score):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Преобразуем словарь навыков в строку
        skills_str = ", ".join([f"{skill}: {'+' if has else '-'}"
                                for skill, has in skills.items()])

        cursor.execute('''
            INSERT INTO candidates (name, job_id, phone, skills, match_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, job_id, phone, skills_str, match_score))

        conn.commit()  # Важно: подтверждаем изменения
        return True
    except Exception as e:
        print(f"Ошибка при добавлении кандидата: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def add_job(job_category, job_title, job_description, job_requirements, job_optionals, job_salary):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO jobs (category, title, description, requirements, optionals, salary)
                    VALUES (?, ?, ?, ?, ?, ?)
            ''', (job_category, job_title, job_description, job_requirements, job_optionals, job_salary))
        conn.commit()
        return True
    except Exception as e:
        print(f"error_add_job: {e}")
        conn.rollback()
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

def get_user_role(telegram_id: int) -> str | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        return result[0] if result else None


def set_user_role(telegram_id: int, role: str, username: str = None, full_name: str = None):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO users (telegram_id, username, full_name, role)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                role = excluded.role,
                username = COALESCE(excluded.username, users.username),
                full_name = COALESCE(excluded.full_name, users.full_name)
        """, (telegram_id, username, full_name, role))
        conn.commit()


def get_user_by_id(telegram_id: int) -> dict | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, telegram_id, username, full_name, role, created_at
            FROM users
            WHERE telegram_id = ?
        """, (telegram_id,))
        row = cursor.fetchone()

        if row:
            return {
                "id": row[0],
                "telegram_id": row[1],
                "username": row[2],
                "full_name": row[3],
                "role": row[4],
                "created_at": row[5],
            }
        return None

def user_exists(telegram_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone() is not None