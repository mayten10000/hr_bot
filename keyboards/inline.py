from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.queries import get_all_jobs

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить вакансию", callback_data="add_job")],
        [InlineKeyboardButton(text="Удалить вакансию", callback_data="delete_job")]
    ])

def job_keyboard(jobs):
    if not jobs:
        return None

    buttons = [
        [InlineKeyboardButton(text=title, callback_data=f"apply_{id}")]
        for id, title in jobs
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def skills_keyboard(remaining_skills):
    """Создает клавиатуру с кнопками для выбора навыков"""
    buttons = []
    for skill in remaining_skills:
        # Добавляем кнопки "+" и "-" для каждого навыка
        buttons.append([
            InlineKeyboardButton(text=f"{skill} ✅", callback_data=f"skill_{skill}_yes"),
            InlineKeyboardButton(text=f"{skill} ❌", callback_data=f"skill_{skill}_no")
        ])
    # Добавляем кнопку "Готово" только если есть навыки
    if remaining_skills:
        buttons.append([InlineKeyboardButton(text="Готово", callback_data="submit_skills")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_candidates_keyboard(candidates):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"❌ {c[1]}", callback_data=f"delete_candidate_{c[0]}")] for c in candidates
    ])
