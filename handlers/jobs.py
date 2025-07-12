from mailbox import Message

from aiogram import Router, types, F
from aiogram.types import CallbackQuery
from database.queries import get_all_jobs, delete_job, get_category_jobs, get_job_details
from keyboards.inline import job_keyboard, delete_job_keyboard, get_categories_keyboard, get_job_details_keyboard
from aiogram.filters import Command
from config import Config, load_config
import logging
from filters.filters import IsAdmin

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format
)

router = Router()

@router.message(Command("jobs"))
async def list_jobs(message: types.Message):
    jobs = get_category_jobs()
    await message.answer("category_choice", reply_markup=job_keyboard(jobs))
    
@router.callback_query(F.data == "delete_job")
async def delete_job_callback(callback: CallbackQuery):
    jobs = get_all_jobs()
    del_keyboard = delete_job_keyboard(jobs)
    await callback.message.edit_text('jobs_for_deleting: ', reply_markup=del_keyboard)
    await callback.answer()
    
@router.callback_query(F.data.startswith("delete_"))
async def process_delete_job(callback: CallbackQuery):
    logging.info(f"process_delete_job is started (job_data={callback})")
    job_id = callback.data.split("_")[-1]
    delete_job(job_id)
    logging.info(f"Job (id={job_id} deleted")
    
    jobs = get_all_jobs()
    new_del_keyboard = delete_job_keyboard(jobs)
    await callback.message.edit_text(
        text="jobs_for_deleting",
        reply_markup=new_del_keyboard
    )

@router.message(Command("jobs"))
async def test_jobs(message: types.Message):
    await message.answer("Тест: сработала команда /jobs")

@router.callback_query(((F.data.startswith("category_")) | (F.data == 'jobs')), ~IsAdmin())
async def print_category_jobs(callback: CallbackQuery):
    job_category = callback.data.split("_")[-1]
    logging.info(f"print_category_jobs method is started (job_category={job_category})")
    jobs = get_category_jobs(job_category)
    logging.info(f"category_jobs: {jobs}")
    if jobs:
        await callback.message.edit_text("jobs_choice", reply_markup=job_keyboard(jobs))
    else:
        await callback.message.edit_text("no_category_jobs", reply_markup=job_keyboard(jobs))

@router.callback_query(F.data.startswith("select_"))
async def print_job(callback: CallbackQuery):
    job_id = callback.data.split('_')[-1]
    details = get_job_details(job_id)
    logging.info(f"selected job ({details})")
    text = (
        f"title: {details[1]}\n"
        f"description: {details[2]}\n"
        f"requirements: {details[3]}\n"
        f"optionals: {details[4]}\n"
        f"salary: {details[5]}"
    )
    await callback.message.edit_text(text, reply_markup=get_job_details_keyboard(details[0]))
    await callback.answer()

@router.message(Command("find_job"))
@router.callback_query(F.data == 'categories')
async def print_category_list(obj: CallbackQuery | Message):
    if isinstance(obj, CallbackQuery):
        await obj.message.edit_text("category_choice", reply_markup=get_categories_keyboard())
    else:
        await obj.answer("category_choice", reply_markup=get_categories_keyboard())
