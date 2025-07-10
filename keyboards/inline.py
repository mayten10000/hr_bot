from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.queries import get_all_jobs

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить вакансию", callback_data="add_job")],
        [InlineKeyboardButton(text="Удалить вакансию", callback_data="delete_job")]
    ])

def job_keyboard(jobs):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=job[1], callback_data=f"select_{job[0]}")] for job in jobs
    ])
 
def delete_job_keyboard(jobs):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"❌ {job[1]}", callback_data=f"delete_{job[0]}")] for job in jobs    
    ])

def skills_keyboard(remaining_skills):
    buttons = []
    for skill in remaining_skills:
        buttons.append([
            InlineKeyboardButton(text=f"{skill} +", callback_data=f"skill_{skill}_yes"),
            InlineKeyboardButton(text=f"{skill} -", callback_data=f"skill_{skill}_no")
        ])
    if not remaining_skills:
        buttons.append([InlineKeyboardButton(text="Готово", callback_data="submit_skills")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_candidates_keyboard(candidates):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"❌ {c[1]}", callback_data=f"delete_candidate_{c[0]}")] for c in candidates
    ])
