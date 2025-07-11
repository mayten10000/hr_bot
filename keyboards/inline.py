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
    ] + [[InlineKeyboardButton(text='back_button', callback_data='categories')]])
 
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

def get_categories_keyboard(categories=[]):
    categories = ['IT', 'Medicine', 'Finance', 'ART']
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=category, callback_data=f"category_{category}")] for category in categories
    ])

def get_checking_job_form_keyboard():
    buttons = [
        InlineKeyboardButton(text="yes", callback_data="is_correct_job_form"),
        InlineKeyboardButton(text="no", callback_data="is_not_correct_job_form")
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def get_job_details_keyboard(category):
    buttons = [
        InlineKeyboardButton(text="back_button", callback_data=f'category_{category}')
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])