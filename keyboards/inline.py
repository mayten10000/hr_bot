from Tools.scripts.dutree import store

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from marshmallow.fields import Boolean
from aiogram import Router, F, Dispatcher
from pyexpat.errors import messages

from database.queries import get_all_jobs

router = Router()

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить вакансию", callback_data="add_job")],
        [InlineKeyboardButton(text="Удалить вакансию", callback_data="delete_job")]
    ])

@router.callback_query(F.data.startswith('page:'))
async def paginate_jobs(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split(':')[1])
    storage = state.storage
    key = StorageKey(bot_id=callback.bot.id, chat_id=callback.message.chat.id, user_id=callback.from_user.id)
    data = await storage.get_data(key)

    jobs = data.get("jobs", [])
    ids = data.get("ids", [])
    await callback.message.edit_reply_markup(reply_markup=await job_keyboard_by_id(jobs, ids, page))
    await callback.answer()

def job_keyboard(jobs, page):
    BUTTON_CNT = 10

    start = page * BUTTON_CNT
    end = start + BUTTON_CNT
    page_jobs = jobs[start:end]

    buttons = [
        [InlineKeyboardButton(text = job[1], callback=f'select_{job[0]}')] for job in page_jobs
    ]

    other_buttons = []
    if start > 0:
        other_buttons.append(InlineKeyboardButton(text='<', callback_data=f'page:{page - 1}'))

    other_buttons.append(InlineKeyboardButton(text='back_button', callback_data='categories'))
    if end < len(buttons):
        other_buttons.append(InlineKeyboardButton(text='>', callback_data=f'page:{page + 1}'))
    if other_buttons:
        buttons.append(other_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def job_keyboard_by_id(jobs, ids, page):
    BUTTON_CNT = 10

    start = page * BUTTON_CNT
    end = start + BUTTON_CNT
    page_jobs = jobs[start:end]
    page_ids = ids[start:end]

    buttons = [
        [InlineKeyboardButton(text=job[1], callback_data=f'select_{ID}')] for job, ID in zip(page_jobs, page_ids)
    ]

    other_buttons = []
    if start > 0:
        other_buttons.append(InlineKeyboardButton(text='<', callback_data=f'page:{page - 1}'))

    other_buttons.append(InlineKeyboardButton(text='back_button', callback_data='categories'))

    if end < len(jobs):
        other_buttons.append(InlineKeyboardButton(text='>', callback_data=f'page:{page + 1}'))

    if other_buttons:
        buttons.append(other_buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)

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
    buttons.append([InlineKeyboardButton(text="Готово", callback_data="submit_skills")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_candidates_keyboard(candidates):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"❌ {c[1]}", callback_data=f"delete_candidate_{c[0]}")] for c in candidates
    ])

def get_categories_keyboard(hr_mod: Boolean, categories=[]):
    categories = ['IT', 'Медицина', 'Финансы']
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=category, callback_data=f"category_{category}")] for category in categories
    ])
    if not hr_mod:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text='key_word_search', callback_data='call_bm25')
        ])
    return keyboard

def get_checking_job_form_keyboard():
    buttons = [
        InlineKeyboardButton(text="yes", callback_data="is_correct_job_form"),
        InlineKeyboardButton(text="no", callback_data="is_not_correct_job_form")
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def get_job_details_keyboard(job_id:int,category:str,is_candidate:bool=False) -> InlineKeyboardMarkup:
    keyboardd = []
    if is_candidate:
        keyboardd.append(
            [
                InlineKeyboardButton(
                    text="Откликнуться",
                    callback_data=f"apply_{job_id}"
                )
            ]
        )

    keyboardd.append([
        InlineKeyboardButton(
            text="back_button",
            callback_data=f"category_{category}"
        )
    ])


    return InlineKeyboardMarkup(inline_keyboard=keyboardd)